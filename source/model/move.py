
from math import copysign, cos, sin

from euclid import Vector3

from ..util.vectors import tuple_of_ints


class Orbit(object):

    def __init__(self, size, frequency=0.2):
        self.size = size
        self.frequency = frequency
        self.center = None
        self.last_position = None

    def __call__(self, item, dt, time):
        if item.position != self.last_position:
            self.center = item.position
        offset = (
            sin(time * self.frequency) * self.size[0],
            cos(time * self.frequency) * self.size[1],
            0)
        self.last_position = item.position = self.center + offset



class directed_motion(object):

    SPEED = 0.06

    def __init__(self, world):
        self.world = world
        self.input = None
        self.velocity = None
        self.next_move = None


    def _try_to_move(self, item):
        # not moving and a move has been requested
        destination = item.position + self.next_move
        # TODO: should check all entries in item.bounds + destination,
        # not just { (0,0,0) } + destination
        # is item_at_dest one we can move into? (e.g. exit)
        if self.world.collision.can_move_to(destination):
            self._start_moving(destination, item)
        self.next_move = None


    def _start_moving(self, destination, item):
        self.old_position = tuple(tuple_of_ints(item.position))
        self.destination = destination
        self.world.collision.add_item(destination, item)
        self.velocity = self.next_move * self.SPEED
        self._stop_moving_flag = -copysign(1, sum(self.next_move))


    def _moving(self, item):
        new_position = item.position + self.velocity
        if self._has_reached_destination(new_position):
            self._stop_moving(item)
        else:
            item.position = new_position


    def _has_reached_destination(self, position):
        offset = position - self.destination
        return self._stop_moving_flag != copysign(1, sum(offset))


    def _stop_moving(self, item):
        item.position = self.destination
        self.world.collision.remove_item(self.old_position, item)
        self.velocity = None
        self.next_move = None


    def __call__(self, item, dt, time):
        position = item.position

        if self.input is not None:
            self.next_move = self.input

        if not self.velocity and self.next_move:
            self._try_to_move(item)

        if self.velocity:
            self._moving(item)

