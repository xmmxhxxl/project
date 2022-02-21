from mysqlProject import MysqlClass

mysql = MysqlClass()
data = mysql.select_all("select * from kindTable")

kind = []
label_test = []
labelPrice = {}
for i in data:
    kind.append(i[1])
    label_test.append(i[2])
    labelPrice.update({i[1]: i[3]})
print(kind, label_test)
print(labelPrice)
