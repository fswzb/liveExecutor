# -*- coding: utf-8 -*-
u"""
Created on 2015-12-23

@author: cheng.li
"""

from LiveExecutor.Utilities import sign
from LiveExecutor.Utilities import py_assert


class Order:

    def __init__(self, id, symbol, quantity, direction):

        self.id = id
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction

    @property
    def amount(self):
        return self.quantity * self.direction

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Order({order_id}, `{symbol}`, {quantity}, {direction})"\
            .format(order_id=self.id, symbol=self.symbol, quantity=self.quantity, direction=self.direction)

    def __eq__(self, other):
        return self.id == other.id \
               and self.symbol == other.symbol \
               and self.quantity == other.quantity \
               and self.direction == other.direction


class OrderData:

    def __init__(self, symbol, quantity, direction):

        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction

    def __eq__(self, other):
        return self.symbol == other.symbol \
               and self.quantity == other.quantity \
               and self.direction == other.direction

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "OrderData(`{symbol}`, {quantity}, {direction})"\
            .format(symbol=self.symbol, quantity=self.quantity, direction=self.direction)


class OrderPacket:

    def __init__(self, orders):

        if orders:
            self.direction = orders[0].direction

            for order in orders:
                py_assert(order.direction == self.direction, ValueError, u"指令方向不匹配")

        else:
            self.direction = 1

        self.order_dict = {order.id: order for order in orders}
        self.total_quantity = sum([order.quantity for order in orders])

    @property
    def total_amount(self):
        return self.total_quantity * self.direction

    def cancel_orders(self, target_quantity):

        accumulated = 0
        canceled_orders = []

        for order in self.order_dict.values():
            if accumulated < target_quantity:
                accumulated += order.quantity
                canceled_orders.append(order)
            else:
                return canceled_orders, target_quantity - accumulated

        return canceled_orders, target_quantity - accumulated

    def __getitem__(self, item):
        return self.order_dict[item]

    def __repr__(self):
        return self.order_dict.__repr__()

    def __str__(self):
        return self.order_dict.__str__()


def create_orders(target_portfolio,
                  pre_target_portfolio,
                  outstanding_orders):

    new_orders = []
    cancel_orders = []

    for s in target_portfolio:
        moving_amount = target_portfolio[s] - pre_target_portfolio[s]
        specific_symbol_order_packet = outstanding_orders[s]

        existing_direction = specific_symbol_order_packet.direction

        if moving_amount != 0:
            remaining_quantity = 0
            if sign(moving_amount) == existing_direction:
                if existing_direction == sign(pre_target_portfolio[s]):
                    new_order = OrderData(s, abs(moving_amount), existing_direction)
                    new_orders.append(new_order)
                else:
                    remaining = moving_amount - specific_symbol_order_packet.total_amount
                    if sign(remaining) == sign(moving_amount):
                        new_order = OrderData(s, abs(remaining), existing_direction)
                        new_orders.append(new_order)
                    elif remaining != 0:
                        symbol_canceled_orders, remaining_quantity \
                            = specific_symbol_order_packet.cancel_orders(abs(moving_amount))
                        cancel_orders += symbol_canceled_orders
            else:
                symbol_canceled_orders, remaining_quantity \
                    = specific_symbol_order_packet.cancel_orders(abs(moving_amount))
                cancel_orders += symbol_canceled_orders
            if remaining_quantity < 0:
                new_order = OrderData(s, abs(remaining_quantity), existing_direction)
                new_orders.append(new_order)
            elif remaining_quantity > 0:
                new_order = OrderData(s, remaining_quantity, -existing_direction)
                new_orders.append(new_order)

    return new_orders, cancel_orders
