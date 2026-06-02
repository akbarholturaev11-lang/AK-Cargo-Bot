from aiogram.fsm.state import State, StatesGroup


class AdminAddParcelStates(StatesGroup):
    waiting_for_ai_photo = State()
    waiting_for_client_code = State()
    waiting_for_track_code = State()
    choosing_received_date = State()
    waiting_for_manual_date = State()
    confirming = State()
