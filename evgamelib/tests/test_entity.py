# Tests para evgamelib.entity

import pytest
from evgamelib.entity import Entity, PhysicsEntity, AnimatedEntity


class TestEntity:
    def test_defaults(self):
        e = Entity()
        assert e.x == 0
        assert e.y == 0
        assert e.width == 32
        assert e.height == 32
        assert e.active == True
        assert e.image is None

    def test_custom_init(self):
        e = Entity(10, 20, 16, 8)
        assert e.x == 10
        assert e.y == 20
        assert e.width == 16
        assert e.height == 8

    def test_get_rect(self):
        e = Entity(5, 10, 32, 32)
        rect = e.get_rect()
        assert rect.x == 5
        assert rect.y == 10
        assert rect.width == 32
        assert rect.height == 32

    def test_is_on_screen_visible(self):
        e = Entity(100, 100, 32, 32)
        assert e.is_on_screen(0, 0, 512, 256) == True

    def test_is_on_screen_outside(self):
        e = Entity(600, 100, 32, 32)
        assert e.is_on_screen(0, 0, 512, 256) == False

    def test_is_on_screen_with_margin(self):
        e = Entity(-30, 100, 32, 32)
        assert e.is_on_screen(0, 0, 512, 256, margin=50) == True


class TestPhysicsEntity:
    def test_defaults(self):
        pe = PhysicsEntity()
        assert pe.vel_x == 0
        assert pe.vel_y == 0

    def test_apply_gravity(self):
        pe = PhysicsEntity()
        pe.apply_gravity(1.0, 200)
        assert pe.vel_y == 200

    def test_apply_gravity_max_fall_speed(self):
        pe = PhysicsEntity()
        pe.vel_y = 350
        pe.apply_gravity(1.0, 200, max_fall_speed=400)
        assert pe.vel_y == 400

    def test_check_collision_corners(self):
        pe = PhysicsEntity(0, 0, 32, 32)
        level_map = [
            "################",
            "#              #",
            "################",
        ]
        solid = {'#'}
        # Entity at (0,0) touches # at corners
        assert pe.check_collision_corners(0, 0, level_map, solid,
                                          corners=[(1, 1)]) == True
        # Entity at (32+1, 32+1) is in open space
        assert pe.check_collision_corners(33, 33, level_map, solid,
                                          corners=[(34, 34)]) == False


class TestAnimatedEntity:
    def test_defaults(self):
        ae = AnimatedEntity()
        assert ae.anim_frame == 0
        assert ae.distance_traveled == 0
        assert ae.anim_distance == 8

    def test_advance_animation(self):
        ae = AnimatedEntity()
        ae.images = ["frame0", "frame1"]
        ae.image = ae.images[0]
        ae.advance_animation(10)
        assert ae.anim_frame == 1
        assert ae.image == "frame1"

    def test_advance_animation_wraps(self):
        ae = AnimatedEntity()
        ae.images = ["frame0", "frame1"]
        ae.image = ae.images[0]
        ae.advance_animation(8)  # frame 1
        ae.advance_animation(8)  # frame 0 (wrap)
        assert ae.anim_frame == 0
