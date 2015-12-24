# -*- coding: utf-8 -*-
u"""
Created on 2015-12-23

@author: cheng.li
"""


import unittest
from LiveExecutor.Orders import Order
from LiveExecutor.Orders import OrderData
from LiveExecutor.Orders import OrderPacket
from LiveExecutor.Orders import create_orders


class TestOrders(unittest.TestCase):

    def test_order(self):

        order = Order(1, '600000.xshe', 200, 1)
        self.assertEqual(order.id, 1)
        self.assertEqual(order.symbol, '600000.xshe')
        self.assertTrue(order.direction == 1)
        self.assertEqual(order.amount, 200)

        order = Order(1, '600000.xshg', 200, -1)
        self.assertEqual(order.amount, -200)

    def test_order_data(self):

        order_data = OrderData('600000.xshe', 200, -1)
        self.assertEqual(order_data.symbol, '600000.xshe')
        self.assertEqual(order_data.quantity, 200)
        self.assertEqual(order_data.direction, -1)

    def test_order_packet(self):
        order_list = [Order(1, '000001.xshe', 200, 1),
                      Order(2, '000001.xshe', 300, 1),
                      Order(3, '000001.xshe', 400, 1)]

        order_packet = OrderPacket(order_list)
        canceled_orders, remaining = order_packet.cancel_orders(100)
        self.assertTrue(len(canceled_orders) == 1)
        self.assertTrue(canceled_orders[0].id == 1)
        self.assertEqual(remaining, -100)

        canceled_orders, remaining = order_packet.cancel_orders(200)
        self.assertTrue(len(canceled_orders) == 1)
        self.assertTrue(canceled_orders[0].id == 1)
        self.assertEqual(remaining, 0)

        canceled_orders, remaining = order_packet.cancel_orders(300)
        self.assertTrue(len(canceled_orders) == 2)
        self.assertTrue(canceled_orders[0].id == 1)
        self.assertTrue(canceled_orders[1].id == 2)
        self.assertEqual(remaining, -200)

        canceled_orders, remaining = order_packet.cancel_orders(1000)
        self.assertTrue(len(canceled_orders) == 3)
        self.assertTrue(canceled_orders[0].id == 1)
        self.assertTrue(canceled_orders[1].id == 2)
        self.assertTrue(canceled_orders[2].id == 3)
        self.assertEqual(remaining, 100)

    def test_empty_order_packet(self):
        order_list = []

        order_packet = OrderPacket(order_list)
        canceled_orders, remaining = order_packet.cancel_orders(100)

        self.assertTrue(len(canceled_orders) == 0)
        self.assertEqual(remaining, 100)

    def test_create_orders(self):

        target_portfolio = {'if1506': 6,
                            'if1507': -7}

        pre_target_portfolio = {'if1506': 3,
                                'if1507': -3}

        outstanding_orders = {'if1506': OrderPacket([Order(1, 'if1506', 1, 1)]),
                              'if1507': OrderPacket([Order(2, 'if1507', 1, -1)])}

        new_orders, cancel_orders = create_orders(target_portfolio=target_portfolio,
                                                  pre_target_portfolio=pre_target_portfolio,
                                                  outstanding_orders=outstanding_orders)

        self.assertEqual(len(new_orders), 2)
        self.assertEqual(len(cancel_orders), 0)

        for order in new_orders:
            if order.symbol == 'if1506':
                self.assertEqual(order.quantity, 3)
                self.assertEqual(order.direction, 1)
                continue

            if order.symbol == 'if1507':
                self.assertEqual(order.quantity, 4)
                self.assertEqual(order.direction, -1)
                continue

            raise ValueError(u"新合约{order}与所有当前代码都不匹配".format(order=order))

    def test_create_order_with_lower_new_target(self):

        target_portfolio = {'if1506': 3,
                            'if1507': -3}

        pre_target_portfolio = {'if1506': 6,
                                'if1507': -7}

        outstanding_orders = {'if1506': OrderPacket([Order(1, 'if1506', 1, 1)]),
                              'if1507': OrderPacket([Order(2, 'if1507', 1, -1)])}

        new_orders, cancel_orders = create_orders(target_portfolio=target_portfolio,
                                                  pre_target_portfolio=pre_target_portfolio,
                                                  outstanding_orders=outstanding_orders)

        self.assertEqual(len(new_orders), 2)
        self.assertEqual(len(cancel_orders), 2)

        for order in new_orders:
            if order.symbol == 'if1506':
                self.assertEqual(order.quantity, 2)
                self.assertEqual(order.direction, -1)
                continue

            if order.symbol == 'if1507':
                self.assertEqual(order.quantity, 3)
                self.assertEqual(order.direction, 1)
                continue

            raise ValueError(u"新合约{order}与所有当前代码都不匹配".format(order=order))

        for order in cancel_orders:
            original_remaing_order_packet = outstanding_orders[order.symbol]
            original_order = original_remaing_order_packet[order.id]
            self.assertEqual(original_order, order)

    def test_create_orders_with_several_exist_orders(self):
        target_portfolio = {'if1506': 3,
                            'if1507': -3}

        pre_target_portfolio = {'if1506': 6,
                                'if1507': -7}

        outstanding_orders = {'if1506': OrderPacket([Order(1, 'if1506', 2, 1), Order(2, 'if1506', 2, 1)]),
                              'if1507': OrderPacket([Order(3, 'if1507', 1, -1), Order(4, 'if1507', 2, -1)])}

        new_orders, cancel_orders = create_orders(target_portfolio=target_portfolio,
                                                  pre_target_portfolio=pre_target_portfolio,
                                                  outstanding_orders=outstanding_orders)

        self.assertEqual(len(new_orders), 2)

        for order in new_orders:
            if order.symbol == 'if1506':
                self.assertEqual(order.quantity, 1)
                self.assertEqual(order.direction, 1)
                continue

            if order.symbol == 'if1507':
                self.assertEqual(order.quantity, 1)
                self.assertEqual(order.direction, 1)
                continue

            raise ValueError(u"新合约{order}与所有当前代码都不匹配".format(order=order))

        self.assertEqual(len(cancel_orders), 4)

        for order in cancel_orders:
            original_order = outstanding_orders[order.symbol][order.id]
            self.assertEqual(order, original_order)

    def test_create_orders_with_empty_outstanding_orders(self):
        target_portfolio = {'if1506': 3,
                            'if1507': -7}

        pre_target_portfolio = {'if1506': 6,
                                'if1507': -10}

        outstanding_orders = {'if1506': OrderPacket([]),
                              'if1507': OrderPacket([])}

        new_orders, cancel_orders = create_orders(target_portfolio=target_portfolio,
                                                  pre_target_portfolio=pre_target_portfolio,
                                                  outstanding_orders=outstanding_orders)

        self.assertEqual(len(new_orders), 2)

        for order in new_orders:
            if order.symbol == 'if1506':
                self.assertEqual(order.quantity, 3)
                self.assertEqual(order.direction, -1)
                continue

            if order.symbol == 'if1507':
                self.assertEqual(order.quantity, 3)
                self.assertEqual(order.direction, 1)
                continue

            raise ValueError(u"新合约{order}与所有当前代码都不匹配".format(order=order))

        self.assertEqual(len(cancel_orders), 0)

    def test_create_orders_with_opposite_outstanding_orders(self):
        target_portfolio = {'if1506': 3}

        pre_target_portfolio = {'if1506': 6}

        outstanding_orders = {'if1506': OrderPacket([Order(1, 'if1506', 2, -1)])}

        new_orders, cancel_orders = create_orders(target_portfolio=target_portfolio,
                                                  pre_target_portfolio=pre_target_portfolio,
                                                  outstanding_orders=outstanding_orders)

        self.assertEqual(len(new_orders), 1)
        self.assertEqual(new_orders[0], OrderData('if1506', 1, -1))
        self.assertEqual(len(cancel_orders), 0)

        target_portfolio = {'if1506': 5}

        pre_target_portfolio = {'if1506': 6}

        outstanding_orders = {'if1506': OrderPacket([Order(1, 'if1506', 2, -1)])}

        new_orders, cancel_orders = create_orders(target_portfolio=target_portfolio,
                                                  pre_target_portfolio=pre_target_portfolio,
                                                  outstanding_orders=outstanding_orders)

        self.assertEqual(len(new_orders), 1)
        self.assertEqual(new_orders[0], OrderData('if1506', 1, -1))
        self.assertEqual(len(cancel_orders), 1)
        self.assertEqual(cancel_orders[0], outstanding_orders['if1506'][1])



