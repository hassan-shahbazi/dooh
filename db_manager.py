import json, os, datetime
import pymysql.cursors

class DatabaseManager:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as myfile:
            self.config = json.load(myfile)
        
        self.connections = []
        self.connection_by_country = {}
        
        for connection_config in self.config:
            connection = pymysql.connect(host=connection_config['host'],
                         user=connection_config['user'],
                         password=connection_config['password'],
                         db=connection_config['db'],
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor,
                         autocommit=True)
            self.connections.append(connection)
            
            self.connection_by_country[connection_config['location']] = connection

    def update_all(self, sql, *args): ## update to all db's
        for connection in self.connections:
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(args))

    def get_all(self, sql): ## gets from all db's
        for connection in self.connections:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return json.dumps(cursor.fetchall())

    def update_agency(self, agency_name, location, psw):## register
        sql = "INSERT INTO agency(agency_name, location, psw) VALUES (%s, %s, %s)"
        self.update_all(sql, agency_name, location, psw) ### update all, since it's fully replicated
        
    def update_payment(self, country, amount, status): ## this is useless
        sql_insert = "INSERT INTO payment (amount, status) VALUES (%s, %s)"
        with self.connection_by_country[country].cursor() as cursor:
            cursor.execute(sql_insert, (amount, 'paid'))
            payment_id = cursor.lastrowid
            return payment_id 

    def update_screenorder(self, country, screen_id, order_id):
        sql_insert3 = "INSERT INTO screenorder (screen_id, order_id) VALUES (%s, %s)"
        with self.connection_by_country[country].cursor() as cursor:
            cursor.execute(sql_insert3,(screen_id, order_id))
            

    def update_order(self, country, duration, number_of_repeat, amount,agency_id, screen_type, city_id):
        sql_insert2 = "INSERT INTO orders(duration, number_of_repeat, amount, agency_id, screen_type, city_id) VALUES (%s,%s,%s,%s,%s,%s)"
        with self.connection_by_country[country].cursor() as cursor:
            cursor.execute(sql_insert2,(duration, number_of_repeat, amount, agency_id, screen_type, city_id))
            order_id = cursor.lastrowid
            return order_id ## must return this to insert into screenorders (foreign key constraint)

    def make_order(self, screen_id, agency_id, duration, number_of_repeat, amount, country, screen_type, city_id):
        ##Order and screenorder to current db
        order_id = self.update_order(country, duration, number_of_repeat, amount, agency_id, screen_type, city_id)
        self.update_screenorder(country, screen_id, order_id)

        ## Orders to finland. The finnish db should have id of 1 
        order_id =  self.update_order('FI', duration, number_of_repeat, amount, agency_id, screen_type, city_id)
        
    def get_screens_list(self): ## all screens from all databases
        sql = "SELECT * FROM screen"
        result = []
        for conn in self.connections:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                result += cursor.fetchall()
        
        print(result)
        return json.dumps(result)
        
        
    def get_city_list(self):## all cities
        sql = "SELECT `city_id`, `name`, `country` FROM `city`"
        print(self.get_all(sql))

    def get_orders_by_agency_country(self, agency_id, country):
        with self.connection_by_country[country].cursor() as cursor:
            sql = "SELECT * FROM orders WHERE agency_id = %s"
            cursor.execute(sql, (agency_id))
            result = cursor.fetchall()
            if not result:
                return json.dumps({'status': 'No orders'})
            if result:
                return json.dumps(result)
            
    def get_agency(self, agency_name, password, country): #essentially a login
        with self.connection_by_country[country].cursor() as cursor:
            sql = "SELECT * FROM agency WHERE agency_name=%s"
            cursor.execute(sql, (agency_name))
            result = cursor.fetchone()
            if not result:
                return json.dumps({'status': 'No such agency'})
            if result['psw'] != password:
                return json.dumps({'status': 'Incorrect password'})
            return json.dumps({'status': 'Success', 'id': result['agency_id']})
    
    def get_screens_by_type(self, country, type): 
        with self.connection_by_country[country].cursor() as cursor:
            sql = "SELECT* FROM screen WHERE type = %s"
            cursor.execute(sql, (type))
            result = cursor.fetchall()
            if not result:
                return json.dumps({'status': 'No screens of that type'})  
            if result:
                return json.dumps(result)    

    def get_screens_by_country(self, country):
         with self.connection_by_country[country].cursor() as cursor:
             sql = "SElECT * FROM screen"
             cursor.execute(sql)
             result = cursor.fetchall()
             if not result:
                 return json.dumps({'status': 'No screens'})  
             if result:
                 return json.dumps(result)

