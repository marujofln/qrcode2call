import requests
from nicegui import ui, app, run
from condos import condos

app.add_static_files("/static", "static")


class Dialpad:
    def __init__(self, condo: dict):
        self.condo = condo
        self.destination = ""

    def insert_number(self, number):
        self.destination += str(number)

    def remove_number(self):
        self.destination = self.destination[:-1]

    def setup_gui(self, call_card, unit: str):
        self.call_card = call_card
        self.unit = unit
        self.call_card.clear()

        with self.call_card:
            ui.input().bind_value(self, "destination").props(
                'outlined input-style="text-align:right"'
            ).tailwind("min-w-full")
            with ui.grid(columns=3):
                ui.button("7", on_click=lambda: self.insert_number("7"))
                ui.button("8", on_click=lambda: self.insert_number("8"))
                ui.button("9", on_click=lambda: self.insert_number("9"))
                # ////////////
                # im not sure what is the purpose of this, it doesnt seem to change functionality in a normal calculator
                ui.button("4", on_click=lambda: self.insert_number("4"))
                ui.button("5", on_click=lambda: self.insert_number("5"))
                ui.button("6", on_click=lambda: self.insert_number("6"))
                # ////////////
                ui.button("1", on_click=lambda: self.insert_number("1"))
                ui.button("2", on_click=lambda: self.insert_number("2"))
                ui.button("3", on_click=lambda: self.insert_number("3"))
                # ////////////
                ui.button("<-", on_click=lambda: self.remove_number())
                ui.button("0", on_click=lambda: self.insert_number("0"))
                ui.button("->", on_click=lambda: handle_originate())


async def handle_originate(origin: str, destination: str, condo: str):
    CALL_TIMEOUT = 20

    n = ui.notification(
        "Chamando",
        position="center",
        type="ongoing",
        spinner=True,
    )

    url = f"{condos[condo]['url']}/v1/originate?origin={condos[condo]['origin']}&destination={condos[condo]['destination'][unit]}"
    # url = 'https://httpbin.org/delay/1'
    response = await run.io_bound(
        requests.get,
        url,
        timeout=CALL_TIMEOUT,
        auth=(condos[condo]["username"], condos[condo]["password"]),
        verify=False,
    )

    if response.status_code == 200:
        n.dismiss()
        ui.notify(
            "Chamada realizada com sucesso. Aguarde o atendimento.",
            position="center",
            type="info",
            duration=5000,
        )

    else:
        n.dismiss()
        ui.notify(
            f"Erro {response.status_code} realizando chamada.",
            position="center",
            type="negative",
            duration=5000,
        )


@ui.page("/", name="")
def root():
    ui.label("Bem-vindo ao Gnovit QRCode2Call")
    ui.page_title("Gnovit QRCode2Call")
    with ui.dropdown_button("Selecione o condomínio", auto_close=True):
        for condo in condos.keys():
            ui.item(condo, on_click=lambda: ui.navigate.to(f"/qrcode/{condo}"))


@ui.page("/qrcode/{condo}")
def show_qrcode(condo: str = None):
    if condos.get(condo) is not None:
        # app.url_path_for('static', path=f'{condo}.png')
        with ui.card(align_items="center"):
            ui.label("Escaneie o QRCode para realizar a chamada")
            ui.image(f"/static/{condo}.png")
    else:
        ui.label("Condomínio não encontrado")


@ui.page("/call/{condo}")
async def call(condo: str = None):
    if condo is None or condos.get(condo) is None:
        ui.label("Condomínio não encontrado")
        return
    d = Dialpad(condo)
    call_card = ui.card(align_items="stretch")
    with call_card:
        ui.label("Selecione o destino para chamar:")
        with ui.grid():
            for unit, destination in condos[condo]["destination"].items():
                ui.button(f"{unit}", on_click=lambda: d.setup_gui(call_card, unit))
        # ui.button("Chamar", on_click=handle_originate)
    # handle_originate(condo, unit)


def handle_dialpad(call_card: ui.card, condo: str, unit: str):
    d = Dialpad(origin=condos[condo]["origin"], destination=condos[condo]["destination"][unit])
    d.setup_gui(call_card)

@ui.page("/dialpad")
async def dialpad():
    d = Dialpad()


ui.run(
    title="Gnovit QRCode2Call",
    dark=None,
    language="pt-BR",
    on_air=False,
    port=8000,
    reload=False,
)
