import sqlite3
from sqlite3 import Error
from sqlite3.dbapi2 import connect
import time

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_buy_order(conn, order):
    sql = '''INSERT INTO orders(symbol,openPrice,openTime,stopPrice,lastStopUpdate)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, order)
    conn.commit()
    return cur.lastrowid

def count_open_orders(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders where selled = 0")

    rows = cur.fetchall()
    return len(rows)

def getOpenOrder(conn):
    cur = conn.cursor()
    cur.execute("SELECT id,symbol,stopPrice FROM orders where selled = 0")
    rows = cur.fetchall()
    return rows

def getLastPrice(conn,id):
    cur = conn.cursor()
    cur.execute("SELECT lastStopUpdate FROM orders where id = ?",(id,))
    rows = cur.fetchall()
    return rows[-1][0]

def updateStopPrice(conn, updateOrder):
    sql = ''' UPDATE orders
              SET stopPrice = ?,
              lastStopUpdate = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, updateOrder)
    conn.commit()

def sellOrder(conn, sellOrder):
    sql = ''' UPDATE orders
              SET closePrice = ? ,
                  closeTime = ? ,
                  selled = 1
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, sellOrder)
    conn.commit()

def isExist(conn, symbol):
    cur = conn.cursor()
    cur.execute("SELECT symbol FROM orders where symbol = ? and selled = 0",(symbol,))
    rows = cur.fetchall()
    return len(rows)>0

def delete_all_orders(conn):
    sql = 'DELETE FROM orders'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def allTradeTele(conn):
    cur = conn.cursor()
    cur.execute('SELECT symbol,openPrice,closePrice FROM orders where selled = 1 ORDER BY id DESC')
    rows = cur.fetchall()
    message=""
    if len(rows)==0: return "Satış gerçekleşmemiş"
    for x in rows:
        prof = round((((x[2]*100)/x[1])-100),4)
        alis = str(x[1]).replace(".", "\\.").replace('-','\\-')
        satis = str(x[2]).replace(".", "\\.").replace('-','\\-')
        if prof>0:
            message += str(x[0]) +" %"+str(prof).replace(".", "\\.").replace('-','\\-')+" \U0001F4C8\nAlış: "+alis+"\nSatiş: "+satis+"\n"
        else:
            message += str(x[0]) +" %"+str(prof).replace(".", "\\.").replace('-','\\-')+" \U0001F4C9\nAlış: "+alis+"\nSatiş: "+satis+"\n"
    return message

def profitTele(conn):
    cur = conn.cursor()
    cur.execute('SELECT symbol,openPrice,closePrice FROM orders where selled = 1')
    rows = cur.fetchall()
    if len(rows)==0: return "Satış gerçekleşmemiş"
    totalProf = 0
    for x in rows:
        totalProf += ((x[2]*100)/x[1])-100
    totalProf = totalProf/len(rows)
    if totalProf > 0:
        return "\U00002B06Toplam Ortalama kazanç: %" + str(round(totalProf,4)).replace(".", "\\.").replace('-','\\-')
    else:
        return "\U00002B07Toplam Ortalama kazanç: %" + str(round(totalProf,4)).replace(".", "\\.").replace('-','\\-')

def profit24HTele(conn):
    cur = conn.cursor()
    cur.execute('SELECT symbol,openPrice,closePrice,closeTime FROM orders where selled = 1')
    rows = cur.fetchall()
    totalProf = 0
    rowCount = 0
    for x in rows:
        if x[3]/1000 > time.time()-86400:
            totalProf += ((x[2]*100)/x[1])-100
            rowCount+=1
    if rowCount==0: return "Son 1 günde satış gerçekleşmemiş"
    totalProf = totalProf/rowCount
    if totalProf > 0:
        return "\U00002B061 Günlük Ortalama kazanç: %" + str(round(totalProf,4)).replace(".", "\\.").replace('-','\\-')
    else:
        return "\U00002B071 Günlük Ortalama kazanç: %" + str(round(totalProf,4)).replace(".", "\\.").replace('-','\\-')

def profitCalc(conn,id):
    cur = conn.cursor()
    cur.execute('SELECT openPrice,closePrice FROM orders where id = ?',(id,))
    rows = cur.fetchall()
    message=""
    if len(rows)==0: return " "
    for x in rows:
        prof = round((((x[1]*100)/x[0])-100),4)
        if prof>0:
            message = " %"+str(prof).replace(".", "\\.").replace('-','\\-')
        else:
            message = " %"+str(prof).replace(".", "\\.").replace('-','\\-')
    return message

def stopTele(conn,symbol):
    cur = conn.cursor()
    cur.execute('SELECT symbol,openPrice,stopPrice FROM orders where selled = 0 AND symbol=?',(symbol,))
    rows = cur.fetchall()
    message=""
    if len(rows)==0: return "\U0001F4C8"
    for x in rows:
        alis = str(x[1]).replace(".", "\\.").replace('-','\\-')
        stop = str(x[2]).replace(".", "\\.").replace('-','\\-')
        message += str(x[0]) +"\nAlış: "+alis+"\nStop: "+stop+"\n"
    return message 

sql_create_table = """CREATE TABLE IF NOT EXISTS orders(
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    symbol text NOT NULL,
                                    openPrice real NOT NULL,
                                    openTime integer NOT NULL,
                                    closePrice real DEFAULT NULL,
                                    closeTime integer DEFAULT NULL,
                                    stopPrice integer NOT NULL,
                                    lastStopUpdate integer NOT NULL,
                                    selled integer NOT NULL DEFAULT 0
                                );"""

drop_table = """DROP TABLE orders"""

#con = create_connection("test.db")
#order = (0.0103499,1616635108,76)
#sellOrder(con,order)
#create_buy_order(con,order)
#create_table(con,drop_table)
#create_table(con,sql_create_table)
#findStops(con,12)
#delete_all_orders(con)

#print(profit24HTele(con))