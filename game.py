import arcade as aa
import _locale
import os
import sys

# resource
base_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(base_dir)

_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

# map
map_scale = 0.5

# window
screen_width = int(30 * 64 * map_scale)
screen_height = int(20 * 64 * map_scale)
screen_title = "踩砖块"
screen_color = aa.color.SKY_BLUE

# player
player_move_speed = 5
player_jump_speed = 15
# gravity
gravity = 1

# game status
game_status_image = {
    "游戏中": "空",
    "过关": "images/游戏过关2.png",
    "失败": "空",
    "通关": "images/游戏通关2.png",
}
# starting level
start_level = 1
max_level = 5

bgm = 'sounds/欢快曲.wav'
jump_sound = 'sounds/jump1.wav'

class MyGame(aa.Window):
    def __init__(self):
        super().__init__(screen_width, screen_height, screen_title)
        self.background_color = screen_color
        # levels
        self.level = start_level
        self.bgm = aa.load_sound(bgm)
        self.bgm.play(loop=True)
        self.jump_sound = aa.load_sound(jump_sound)

    def setup(self):
        # load maps
        map_name = f"maps/level{self.level}.tmx"
        self.tile_map = aa.load_tilemap(map_name, scaling=map_scale)
        self.scene = aa.Scene.from_tilemap(self.tile_map)
        # change property
        for brick in self.scene.name_mapping["砖块"]:
            brick.properties["num"] = int(brick.properties["num"])
        # player
        self.player = self.scene.name_mapping["玩家"][0]
        # physic engine
        static = [self.scene.name_mapping["墙"], self.scene.name_mapping["砖块"]]
        # moving platform
        platforms = []
        if self.scene.name_mapping.get("移动的砖块"):
            platforms.append(self.scene.name_mapping["移动的砖块"])
        self.physics_engine = aa.PhysicsEnginePlatformer(self.player, walls=static, gravity_constant=gravity,
                                                         platforms=platforms)
        # whether is on brick
        self.pre_is_on_brick = self.is_on_brick()
        # zero bricks
        self.zero_brick_list = aa.SpriteList()
        # game status
        self.game_status = aa.Sprite()
        self.game_status.position = screen_width // 2, screen_height // 2
        self.game_status.scale = 0.5
        self.game_status.text = "游戏中"

        # player camera
        self.player_camera = aa.Camera(screen_width, screen_height)
        # game status camera
        self.game_status_camera = aa.Camera(screen_width, screen_height)

    def on_draw(self):
        self.clear()
        if self.tile_map.width * self.tile_map.tile_width * map_scale > screen_width:
            self.player_camera.use()
        self.scene.draw()
        self.draw_brick_num()
        self.game_status_camera.use()
        self.game_status.draw()

    def on_update(self, time):
        self.physics_engine.update()
        self.deal_jump()
        if self.game_status.text == "游戏中":
            self.deal_game_status()
        self.move_player_camera()

    def on_key_press(self, key, modifiers):
        if key == aa.key.UP and self.physics_engine.can_jump():
            self.player.change_y = player_jump_speed
            self.jump_sound.play()
        elif key == aa.key.LEFT:
            self.player.change_x = -player_move_speed
        elif key == aa.key.RIGHT:
            self.player.change_x = player_move_speed

    def on_key_release(self, key, modifiers):
        if key in [aa.key.UP]:
            self.player.change_y = 0
        elif key in [aa.key.LEFT, aa.key.RIGHT]:
            self.player.change_x = 0

    def draw_brick_num(self):
        bricks = self.scene.name_mapping["砖块"]
        for brick in bricks:
            n = aa.Text(str(brick.properties["num"]), brick.center_x, brick.center_y, aa.color.BROWN,
                        font_size=15, anchor_x="center", anchor_y="center")
            n.draw()

    def is_on_brick(self):
        self.player.center_y -= 1
        result = self.player.collides_with_list(self.scene.name_mapping["砖块"])
        self.player.center_y += 1

        return result

    def deal_jump(self):
        current = self.is_on_brick()
        if not self.pre_is_on_brick and current:
            # interaction with bricks
            for brick in current:
                brick.properties["num"] -= 1
                # change brick
                brick_image = f"images/brick{brick.properties['num']}.png"
                brick.texture = aa.load_texture(brick_image)
                # statistic zero bricks
                if brick.properties["num"] == 0:
                    self.zero_brick_list.append(brick)
        # delete zero bricks
        elif self.pre_is_on_brick and not current:
            for brick in self.zero_brick_list:
                brick.kill()
        self.pre_is_on_brick = current

    def deal_game_status(self):
        # pass
        if len(self.scene.name_mapping["砖块"]) == 0:
            self.game_status.text = "过关"
            # win
            if self.level < max_level:
                self.level += 1
                self.setup()
            else:
                self.game_status.text = "通关"
        # lose
        if self.player.top < 0 or self.is_collide_barrier():
            self.game_status.text = "失败"
            self.setup()
        # change game status pic
        if game_status_image[self.game_status.text] != "空":
            self.game_status.texture = aa.load_texture(game_status_image[self.game_status.text])

    def is_collide_barrier(self):
        if self.scene.name_mapping.get("障碍物"):
            result = self.player.collides_with_list(self.scene.name_mapping["障碍物"])
            return result

    def move_player_camera(self):
        camera_x = self.player.center_x - screen_width // 2
        camera_y = self.player.center_y - screen_height // 2
        # limit camera position
        if camera_x < 0:
            camera_x = 0
        if camera_y < 0:
            camera_y = 0
        camera_pos = camera_x, camera_y
        self.player_camera.move(camera_pos)


w = MyGame()
w.setup()
w.run()
