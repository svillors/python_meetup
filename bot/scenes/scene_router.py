class SceneRouter:
    scenes = {}

    @classmethod
    def get(cls, name):
        scene_cls = cls.scenes.get(name)
        if not scene_cls:
            raise KeyError(f'сцена "{name}" не найдена')
        return scene_cls()
