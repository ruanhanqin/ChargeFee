#!/usr/bin/env python
# -*-encoding: utf-8-*-

import xlrd
import sqlite3
from datetime import datetime
import MySQLdb


class UpdateDatabase(object):
    def __init__(self):
        self.arrears = []  # 欠费列表
        self.bill = []  # 收费列表

    def read_excel(self, filename=None, types=None):
        """
        读取欠费excel表
        :param filename: 文件名
        :param types: 类型
        :return:
        """
        excel = xlrd.open_workbook(filename)
        sheet = excel.sheet_by_index(0)
        rows = sheet.nrows
        if types == 0:  # QIANF表
            for i in range(1, rows):
                arrears_info = dict()
                arrears_info['account_number'] = sheet.row_values(i)[1:2][0]
                arrears_info['account_name'] = sheet.row_values(i)[2:3][0]
                arrears_info['address'] = sheet.row_values(i)[4:5][0]
                arrears_info['arrears'] = ''
                arrears_info['arrears_time'] = ''
                arrears_info['write_book'] = sheet.row_values(i)[11:12][0]
                arrears_info['user_phone'] = sheet.row_values(i)[17:18][0]
                arrears_info['bill_manager'] = sheet.row_values(i)[18:19][0]
                self.arrears.append(arrears_info)
        elif types == 1:  # SHOUF表
            for i in range(1, rows):
                bill_info = dict()
                bill_info['account_number'] = sheet.row_values(i)[0:1][0]
                bill_info['arrears'] = sheet.row_values(i)[5:6][0]
                bill_info['arrears_time'] = sheet.row_values(i)[12:13][0]
                self.bill.append(bill_info)
        elif types == 2:
            for i in range(1, rows):
                arrears_info = dict()
                arrears_info['write_book'] = sheet.row_values(i)[0:1][0]
                arrears_info['account_number'] = sheet.row_values(i)[1:2][0]
                arrears_info['account_name'] = sheet.row_values(i)[2:3][0]
                arrears_info['arrears'] = sheet.row_values(i)[3:4][0]
                arrears_info['arrears_time'] = sheet.row_values(i)[4:5][0]
                arrears_info['bill_manager'] = sheet.row_values(i)[5:6][0]
                arrears_info['address'] = ''
                arrears_info['user_phone'] = ''
                self.arrears.append(arrears_info)
            print(self.arrears)
        return None

    def merge(self):
        """合并两个表"""
        for index, _arrears in enumerate(self.arrears):
            for _bill in self.bill:
                if _bill['account_number'] == _arrears['account_number']:
                    self.arrears[index]['arrears'] = _bill['arrears']
                    self.arrears[index]['arrears_time'] = _bill['arrears_time']
                    break

    def update_database(self):
        """插入数据库"""
        insert_sql = """INSERT INTO management_charge(write_book, account_number, account_name, address, user_phone, arrears, 
                        arrears_time, in_arrears, bill_manager_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        # conn = sqlite3.connect('../db.sqlite3')

        conn = MySQLdb.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='root',
            db='chargefee',
            charset='utf8'
        )
        cursors = conn.cursor()
        for arrears_item in self.arrears:
            try:
                rows = cursors.execute(
                    "select id from users_userprofile where name='{}'".format(arrears_item['bill_manager']))
                result = rows.fetchone()[0]
            except Exception as e:
                result = 1
            cursors.execute(insert_sql, (
                arrears_item['write_book'], arrears_item['account_number'], arrears_item['account_name'],
                arrears_item['address'], arrears_item['user_phone'], float(arrears_item['arrears']),
                datetime.strptime(arrears_item['arrears_time'], '%Y-%m-%d %H:%M'), '欠费', result
            ))
            conn.commit()
        conn.close()


if __name__ == "__main__":
    arrears = UpdateDatabase()
    # arrears.read_excel(filename='QIANF.xls', types=0)
    # arrears.read_excel(filename='SHOUF1.xls', types=1)
    # arrears.read_excel(filename='SHOUF2.xls', types=1)
    # arrears.read_excel(filename='SHOUF3.xls', types=1)
    # arrears.merge()
    arrears.read_excel(filename='qf.xlsx', types=2)
    arrears.update_database()
