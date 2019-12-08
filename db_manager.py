import json, os, datetime
import pymysql.cursors

class DatabaseManager:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as myfile:
            self.config = json.load(myfile)
        
        self.connections = []
        self.connection_by_country = {}
        self.connection_by_city_id = {}
        
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
            self.connection_by_city_id[connection_config['id']] = connection

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

    def get_screens(self, city_id): ## screens by city
        sql = "SELECT * FROM screen WHERE city_id=%s"
        with self.connection_by_city_id[int(city_id)].cursor() as cursor:
            cursor.execute(sql, (city_id))
            return json.dumps(cursor.fetchall())

    def update_payment(self, city_id, amount, status):
        sql_insert = "INSERT INTO payment (amount, status) VALUES (%s, %s)"
        with self.connection_by_city_id[int(city_id)].cursor() as cursor:
            cursor.execute(sql_insert, (amount, 'paid'))
            payment_id = cursor.lastrowid
            return payment_id 

    def update_screenorder(self, city_id, screen_id, order_id):
        sql_insert3 = "INSERT INTO screenorder (screen_id, order_id) VALUES (%s, %s)"
        with self.connection_by_city_id[int(city_id)].cursor() as cursor:
            cursor.execute(sql_insert3,(screen_id, order_id))
            

    def update_order(self, city_id, duration, number_of_repeat, payment_id,agency_id):
        sql_insert2 = "INSERT INTO orders(duration, number_of_repeat, payment_id, agency_id) VALUES (%s,%s,%s,%s)"
        with self.connection_by_city_id[int(city_id)].cursor() as cursor:
            cursor.execute(sql_insert2,(duration, number_of_repeat, payment_id, agency_id))
            order_id = cursor.lastrowid
            return order_id

    def make_order(self, screen_id, agency_id, duration, number_of_repeat, amount, city_id):
        ## orders, payments, screenorders to current db
        payment_id = self.update_payment(city_id, amount, 'paid')
        print(payment_id)
        order_id = self.update_order(city_id, duration, number_of_repeat, payment_id, agency_id)
        print(order_id)
        self.update_screenorder(city_id, screen_id, order_id)

        ## Orders and payments to finland. The finnish db should have id of 1 (should probably make it so this reads the id from the config.json)
        payment_id =  self.update_payment(1, amount, 'paid')
        order_id =  self.update_order(1, duration, number_of_repeat, payment_id, agency_id)
        
    def get_screens_list(self): ## all screens 
        sql = "SELECT * FROM screen"
        result = []
        for conn in self.connections:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                result += cursor.fetchall()
        
        print(result)
        return json.dumps(result)
        
        
    def get_city_list(self):## all screens
        sql = "SELECT `city_id`, `name`, `country` FROM `city`"
        print(self.get_all(sql))
        
            
    def get_agency(self, agency_name, password, city_id): #essentially a login
        with self.connection_by_city_id[int(city_id)].cursor() as cursor:
            sql = "SELECT * FROM agency WHERE agency_name=%s"
            cursor.execute(sql, (agency_name))
            result = cursor.fetchone()
            if not result:
                return json.dumps({'status': 'No such agency'})
            if result['psw'] != password:
                return json.dumps({'status': 'Incorrect password'})
            return json.dumps({'status': 'Success', 'id': result['agency_id']})
            
 
    
db=DatabaseManager()
##db.get_screens_list()
##db.get_screens(1)
db.update_agency('Franco Fancon poika Franco','SPA','123')
##print(db.get_agency('Benis :DD', '12', 1))
db.make_order(3,1,2.0,2,3,2)
db.get_city_list()