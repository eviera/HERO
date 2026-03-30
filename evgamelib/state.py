# evgamelib - Maquina de estados


class GameState:
    """Clase base para un estado del juego."""

    def enter(self, game):
        """Se llama al entrar al estado."""
        pass

    def exit(self, game):
        """Se llama al salir del estado."""
        pass

    def handle_event(self, event, game):
        """Procesa un evento de pygame."""
        pass

    def update(self, dt, game):
        """Actualiza logica del estado."""
        pass

    def render(self, game):
        """Renderiza el estado."""
        pass


class StateMachine:
    """Maneja transiciones entre GameStates."""

    def __init__(self):
        self.states = {}       # name -> GameState instance
        self.current = None
        self.current_name = None

    def add(self, name, state):
        """Registra un estado."""
        self.states[name] = state

    def switch(self, name, game=None):
        """Cambia al estado indicado."""
        if self.current:
            self.current.exit(game)
        self.current_name = name
        self.current = self.states.get(name)
        if self.current:
            self.current.enter(game)

    def handle_event(self, event, game=None):
        """Delega evento al estado actual."""
        if self.current:
            self.current.handle_event(event, game)

    def update(self, dt, game=None):
        """Delega update al estado actual."""
        if self.current:
            self.current.update(dt, game)

    def render(self, game=None):
        """Delega render al estado actual."""
        if self.current:
            self.current.render(game)
