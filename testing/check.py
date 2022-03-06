from src.app_util import Modal, TextInputStyle


def test_modal_init():
    m = Modal("Title", "custom_id")
    m.add_field("field1", "value1", style=TextInputStyle.PARAGRAPH)


    @m.callback
    def callback_func(a):
        print(a)


    print(m.__callback__)
    print(m.data)


test_modal_init()
