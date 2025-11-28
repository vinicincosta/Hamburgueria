import token
import urllib
import uuid
from cmath import e
from http.client import responses
from idlelib.browser import is_browseable_extension
from tkinter.constants import CENTER

import flet as ft
from flet import AppBar, Text, View
from flet.core.alignment import top_left, bottom_center
from flet.core.border_radius import horizontal
from flet.core.box import BoxDecoration
from flet.core.buttons import ButtonStyle, RoundedRectangleBorder
from flet.core.colors import Colors
from flet.core.dropdown import Option
from flet.core.elevated_button import ElevatedButton
from flet.core.icons import Icons
from flet.core.text_style import TextStyle, TextThemeStyle
from flet.core.theme import TextTheme
from flet.core.types import FontWeight, MainAxisAlignment, CrossAxisAlignment

from urllib.parse import urlparse, parse_qs


from routes import *


def main(page: ft.Page):
    # Configurações
    page.title = "Exemplo de Login"
    page.theme_mode = ft.ThemeMode.LIGHT  # ou ft.ThemeMode.DARK
    page.window.width = 375
    page.window.height = 667
    page.fonts = {
        "Playfair Display": "https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap"
    }
    # Funções

    def click_login(e):
        loading_indicator.visible = True
        page.update()

        resultado_pessoas = listar_pessoas()
        print(f'Resultado: {resultado_pessoas}')

        if not input_email.value or not input_senha.value:
            snack_error('Email e senha são obrigatórios.')
            page.update()
            return

        token, papel, nome, error = post_login(input_email.value, input_senha.value)

        print(f"Token: {token}, Papel: {papel}, Nome: {nome}, Erro: {error}")

        # Verifica se o usuário está inativo
        for pessoa in resultado_pessoas:
            if pessoa['email'] == input_email.value:
                if pessoa['status_pessoa'] == "Inativo":
                    snack_error('Erro: usuário inativo.')
                    page.update()
                    return

        if token:
            snack_sucesso(f'Login bem-sucedido, {nome} ({papel})!')
            print(f"Papel do usuário: {papel}, Nome: {nome}")
            page.client_storage.set('token', token)
            page.client_storage.set('papel', papel)

            #  Salva o ID da pessoa logada na sessão
            for pessoa in resultado_pessoas:
                if pessoa['email'] == input_email.value:
                    page.session.set("pessoa_id", pessoa["id_pessoa"])
                    print("pessoa_id salvo na sessão:", pessoa["id_pessoa"])
                    break

            input_email.value = ''
            input_senha.value = ''

            if papel == "cliente":
                page.go("/presencial_delivery")
            elif papel == "garcom":
                page.go("/mesa")
            else:
                snack_error('Erro: Papel do usuário desconhecido.')
        else:
            snack_error(f'Erro: {error}')

        page.update()

    def cadastro_click_user(e):
        try:
            # Se não for admin, define como cliente
            papel = input_papel.value
            if papel != "admin":
                papel = "cliente"

            pessoa, error = post_pessoas(
                input_nome.value,
                input_cpf.value,
                papel,  # papel já validado
                input_senha_cadastro.value,
                float(slider_salario.value or 0),  # garante valor numérico
                input_email_cadastrado.value,
                input_status_user.value,
            )

            if pessoa:
                snack_sucesso(f'Usuário criado com sucesso! ID: {pessoa["user_id"]}')
                # Resetar os campos
                input_nome.value = ""
                input_cpf.value = ""
                input_email_cadastrado.value = ""
                input_senha_cadastro.value = ""
                input_status_user.value = None
                input_papel.value = None
                slider_salario.value = 0  # volta para o mínimo
                txt_salario.value = "SALÁRIO: 0"
            else:
                snack_error(f'Erro: {error}')

        except Exception as ex:
            snack_error(f"Erro inesperado: {ex}")

        page.go("/login")
        page.update()
        page.update()

    def display_slider_salario(e):
        txt_salario.value = f'SALÁRIO: {int(e.control.value)}'
        page.update()

    def click_logout(e):
        page.client_storage.remove("access_token")
        snack_sucesso("logout realizado com sucesso")
        page.go("/")

    def snack_sucesso(texto: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=Colors.GREEN
        )
        page.snack_bar.open = True
        page.overlay.append(page.snack_bar)

    def snack_error(texto: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=Colors.RED
        )
        page.snack_bar.open = True
        page.overlay.append(page.snack_bar)

    def atualizar_lanches_estoque():
        token = page.client_storage.get('token')
        insumos = listar_insumos(token)  # pega todos os insumos

        for insumo in insumos:
            id_insumo = insumo["id_insumo"]
            # Chama a rota de update para cada insumo
            update_insumo(id_insumo)

    def atualizar_bebidas_estoque():
        token = page.client_storage.get('token')
        bebidas = listar_bebidas(token)  # pega todos os insumos

        for bebida in bebidas:
            id_bebida = bebida["id_bebida"]
            # Chama a rota de update para cada insumo
            update_bebida(id_bebida)

    # FUNÇÕES CARDÁPIO
    # def cardapio_porcoes(e):
    #     lv_porcoes.controls.clear()
    #
    #     # Primeiro atualiza o estoque de todos os insumos
    #     atualizar_lanches_estoque()
    #
    #     token = page.client_storage.get('token')
    #     resultado_lanches = listar_lanche(token)
    #
    #     print(f'Resultado dos lanches: {resultado_lanches}')
    #
    #     for lanche in resultado_lanches:
    #         # Mostra só os ativos
    #         if lanche["disponivel"] == True:
    #             lv_porcoes.controls.append(
    #                 ft.Card(
    #                     content=ft.Container(
    #                         content=ft.Row(
    #                             [
    #                                 ft.Image(src="imagemdolanche.png", height=100),
    #                                 ft.Column(
    #                                     [
    #                                         ft.Text(f'{lanche["nome_lanche"]}', color=Colors.ORANGE_900),
    #                                         ft.Text(f'R$ {lanche["valor_lanche"]:.2f}', color=Colors.YELLOW_900),
    #                                         ft.Text(f'{lanche["descricao_lanche"]}',
    #                                                 color=Colors.YELLOW_800, width=200),
    #                                         ft.ElevatedButton(
    #                                             "Finalizar Pedido",
    #                                             on_click=lambda e: page.open(dlg_modal),
    #                                             style=ft.ButtonStyle(
    #                                                 bgcolor=Colors.ORANGE_700,
    #                                                 color=Colors.BLACK,
    #                                                 padding=15,
    #                                                 shape={"": ft.RoundedRectangleBorder(radius=10)}
    #                                             )
    #                                         )
    #                                     ]
    #                                 ),
    #                             ]
    #                         ),
    #                         bgcolor=Colors.BLACK,
    #                         height=180,
    #                         border_radius=10,
    #                         border=ft.Border(
    #                             top=ft.BorderSide(2, color=Colors.WHITE),
    #                             bottom=ft.BorderSide(2, color=Colors.WHITE)
    #                         ),
    #                     ),
    #                     shadow_color=Colors.YELLOW_900
    #                 )
    #             )
    #
    #     page.update()

    def cardapio_bebidas(e):
        lv_bebidas.controls.clear()

        # Primeiro atualiza o estoque de todos os insumos
        atualizar_bebidas_estoque()

        token = page.client_storage.get('token')
        resultado_bebidas = listar_bebidas(token)

        print(f'Resultado das bebidas: {resultado_bebidas}')

        for bebida in resultado_bebidas:
            if bebida["status_bebida"] == True:
            # Mostra só os ativos
                lv_bebidas.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Image(src="istockphoto-459361585-170667a.jpg", height=100),
                                    ft.Column(
                                        [
                                            ft.Text(f'{bebida["nome_bebida"]}', color=Colors.ORANGE_900, font_family="Arial", size=18),
                                            ft.Text(f'R$ {bebida["valor"]:.2f}', color=Colors.YELLOW_900, font_family="Arial", size=18),

                                            ft.Text(f'{bebida["descricao"]}',
                                                    color=Colors.YELLOW_800, width=200, font_family="Aharoni", size=13),
                                            ft.ElevatedButton(
                                                "Finalizar Pedido",
                                                on_click=lambda e: page.open(dlg_modal),
                                                style=ft.ButtonStyle(
                                                    bgcolor=Colors.ORANGE_700,
                                                    color=Colors.BLACK,
                                                    padding=15,
                                                    shape={"": ft.RoundedRectangleBorder(radius=10)}
                                                )
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            bgcolor=Colors.BLACK,
                            height=180,
                            border_radius=10,
                            border=ft.Border(
                                top=ft.BorderSide(2, color=Colors.WHITE),
                                bottom=ft.BorderSide(2, color=Colors.WHITE)
                            ),
                        ),
                        shadow_color=Colors.YELLOW_900
                    )
                )

        page.update()

    def cardapio(e):
        lv_lanches.controls.clear()

        # Primeiro atualiza o estoque de todos os insumos
        atualizar_lanches_estoque()

        token = page.client_storage.get('token')
        resultado_lanches = listar_lanche(token)

        print(f'Resultado dos lanches: {resultado_lanches}')

        for lanche in resultado_lanches:
            # Mostra só os ativos
            if lanche["disponivel"] == True:
                lv_lanches.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Image(src="imagemdolanche.png", height=100),
                                    ft.Column(
                                        [
                                            ft.Text(f'{lanche["nome_lanche"]}', color=Colors.ORANGE_900, font_family="Arial", size=18),
                                            ft.Text(f'R$ {lanche["valor_lanche"]:.2f}', color=Colors.YELLOW_900, font_family="Arial", size=18),
                                            ft.Text(f'{lanche["descricao_lanche"]}',
                                                    color=Colors.YELLOW_800, width=200, font_family="Aharoni", size=13),
                                            ft.ElevatedButton(
                                                "Finalizar Pedido",
                                                on_click=lambda e: page.open(dlg_modal),
                                                style=ft.ButtonStyle(
                                                    bgcolor=Colors.ORANGE_700,
                                                    color=Colors.BLACK,
                                                    padding=15,
                                                    shape={"": ft.RoundedRectangleBorder(radius=10)}
                                                )
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            bgcolor=Colors.BLACK,
                            height=180,
                            border_radius=10,
                            border=ft.Border(
                                top=ft.BorderSide(2, color=Colors.WHITE),
                                bottom=ft.BorderSide(2, color=Colors.WHITE)
                            ),
                        ),
                        shadow_color=Colors.YELLOW_900
                    )
                )

        page.update()

    def cardapio_delivery(e):
        lv_lanches.controls.clear()  # limpa antes de carregar

        # Primeiro atualiza o estoque de todos os insumos
        atualizar_lanches_estoque()

        token = page.client_storage.get('token')
        resultado_lanches = listar_lanche(token)
        print(f'Resultado dos lanches: {resultado_lanches}')

        # garante que o carrinho exista
        if page.client_storage.get("carrinho") is None:
            page.client_storage.set("carrinho", [])



        def adicionar_ao_carrinho(lanche):
            carrinho = page.client_storage.get("carrinho") or []
            if isinstance(carrinho, str):
                import json
                carrinho = json.loads(carrinho)

            novo_item = {
                "tipo": "lanche",
                "id_lanche": lanche.get("id_lanche"),
                "nome_lanche": lanche.get("nome_lanche"),
                "valor_lanche": float(lanche.get("valor_lanche", 0.0)),
                "descricao_lanche": lanche.get("descricao_lanche", "")
            }

            carrinho.append(novo_item)
            page.client_storage.set("carrinho", carrinho)

            snack_sucesso(f"{lanche.get('nome_lanche', 'Lanche')} adicionado ao carrinho!")
            page.update()
            print(f"Carrinho atualizado: {carrinho}")

        # renderiza cada lanche
        for lanche in resultado_lanches:
            if lanche["disponivel"] == True:
                lv_lanches.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Image(src="imagemdolanche.png", height=70),
                                    ft.Column(
                                        [
                                            ft.Text(f'{lanche["nome_lanche"]}', color=Colors.ORANGE_900, font_family="Arial", size=18),
                                            ft.Text(f'R$ {lanche["valor_lanche"]:.2f}', color=Colors.YELLOW_900, font_family="Arial", size=18),

                                            ft.Text(f'{lanche["descricao_lanche"]}',
                                                    color=Colors.YELLOW_800, width=200, font_family="Aharoni", size=13),
                                            ft.ElevatedButton(
                                                "Adicionar ao Carrinho",
                                                on_click=lambda e, l=lanche: adicionar_ao_carrinho(l),
                                                style=ft.ButtonStyle(
                                                    bgcolor=Colors.ORANGE_700,
                                                    color=Colors.BLACK,
                                                    padding=15,
                                                    shape={"": ft.RoundedRectangleBorder(radius=10)}
                                                )
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            bgcolor=Colors.BLACK,
                            height=180,
                            border_radius=10,
                            border=ft.Border(
                                top=ft.BorderSide(2, color=Colors.WHITE),
                                bottom=ft.BorderSide(2, color=Colors.WHITE)
                            ),
                        ),
                        shadow_color=Colors.YELLOW_900
                    )

                )

        # Botão "Ver Carrinho" no final da tela
        lv_lanches.controls.append(
            ft.Container(
                content=ft.ElevatedButton(
                    "Ver Carrinho",
                    on_click=lambda e: page.go("/carrinho"),
                    style=ft.ButtonStyle(
                        bgcolor=Colors.YELLOW_700,
                        color=Colors.BLACK,
                        padding=15,
                        shape={"": ft.RoundedRectangleBorder(radius=10)}
                    )
                ),
                padding=20
            )
        )

        page.update()

    def cardapio_delivery_bebida(e):
        lv_bebidas.controls.clear()

        # Primeiro atualiza o estoque de todos os insumos
        token = page.client_storage.get('token')
        resultado_bebidas = listar_bebidas(token)
        print(f'Resultado das bebidas: {resultado_bebidas}')

        # garante que o carrinho exista
        if page.client_storage.get("carrinho") is None:
            page.client_storage.set("carrinho", [])

        def adicionar_ao_carrinho(bebida):
            # Garante que o carrinho é sempre uma lista válida
            carrinho = page.client_storage.get("carrinho") or []

            # Se o carrinho vier em formato JSON (string), converte para lista
            if isinstance(carrinho, str):
                try:
                    import json
                    carrinho = json.loads(carrinho)
                except:
                    carrinho = []

            # Monta um dicionário limpo apenas com os campos necessários
            novo_item = {
                "tipo": "bebida",
                "id_bebida": bebida.get("id_bebida"),
                "nome_bebida": bebida.get("nome_bebida"),
                "valor": float(bebida.get("valor", 0.0)),
                "descricao": bebida.get("descricao", "")
            }

            # Adiciona o novo item no carrinho
            carrinho.append(novo_item)
            page.client_storage.set("carrinho", carrinho)

            # Feedback visual
            snack_sucesso(f"{bebida.get('nome_bebida', 'Bebida')} adicionada ao carrinho!")
            page.update()

            print(f"Carrinho atualizado: {carrinho}")

        # renderiza cada lanche
        for bebida in resultado_bebidas:
            if bebida["status_bebida"] == True:
                lv_bebidas.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Image(src="ChatGPT Image 14 de nov. de 2025, 15_44_16.png", height=70),
                                    ft.Column(
                                        [
                                            ft.Text(f'{bebida["nome_bebida"]}', color=Colors.ORANGE_900, font_family="Arial", size=17),
                                            ft.Text(f'R$ {bebida["valor"]:.2f}', color=Colors.YELLOW_900, font_family="Arial", size=15),

                                            ft.Text(f'{bebida["descricao"]}',
                                                    color=Colors.YELLOW_800, width=200, font_family="Aharoni", size=13),

                                            ft.ElevatedButton(
                                                "Adicionar ao Carrinho",
                                                on_click=lambda e, b=bebida: adicionar_ao_carrinho(b),
                                                style=ft.ButtonStyle(
                                                    bgcolor=Colors.ORANGE_700,
                                                    color=Colors.BLACK,
                                                    padding=15,
                                                    shape={"": ft.RoundedRectangleBorder(radius=10)}
                                                )
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            bgcolor=Colors.BLACK,
                            height=180,
                            border_radius=10,
                            border=ft.Border(
                                top=ft.BorderSide(2, color=Colors.WHITE),
                                bottom=ft.BorderSide(2, color=Colors.WHITE)
                            ),
                        ),
                        shadow_color=Colors.YELLOW_900
                    )

                )
                page.update()
    # ***********************************************/***************


    # Função para remover item do carrinho
    def remover_item(index):
        carrinho = page.client_storage.get("carrinho") or []

        if isinstance(carrinho, str):
            try:
                carrinho = json.loads(carrinho)
            except:
                carrinho = []

        # Filtra somente os itens válidos
        carrinho = [i for i in carrinho if i.get("id_lanche") or i.get("id_bebida")]

        # Proteção contra índices inválidos
        if index < 0 or index >= len(carrinho):
            snack_error("Índice de lanche inválido.")
            return

        # Verifica se o item é mesmo um lanche antes de remover
        if carrinho[index].get("tipo") != "lanche":
            snack_error("Esse item não é um lanche.")
            return

        # Remove o lanche
        removido = carrinho.pop(index)
        snack_sucesso(f"Lanche '{removido.get('nome_lanche', 'sem nome')}' removido do carrinho!")

        # Atualiza o armazenamento e recarrega a tela
        page.client_storage.set("carrinho", carrinho)
        carrinho_view(None)

    def remover_item_b(index):
        carrinho = page.client_storage.get("carrinho") or []

        if isinstance(carrinho, str):
            try:
                carrinho = json.loads(carrinho)
            except:
                carrinho = []

        carrinho = [i for i in carrinho if i.get("id_lanche") or i.get("id_bebida")]

        if index < 0 or index >= len(carrinho):
            snack_error("Índice de bebida inválido.")
            return

        if carrinho[index].get("tipo") != "bebida":
            snack_error("Esse item não é uma bebida.")
            return

        removido = carrinho.pop(index)
        snack_sucesso(f"Bebida '{removido.get('nome_bebida', 'sem nome')}' removida do carrinho!")

        page.client_storage.set("carrinho", carrinho)
        carrinho_view(None)

    def carrinho_view(e):
        lv_carrinho.controls.clear()

        # --- Recupera e garante lista válida ---
        carrinho = page.client_storage.get("carrinho") or []
        if isinstance(carrinho, str):
            try:
                carrinho = json.loads(carrinho)
            except:
                carrinho = []

        # --- Limpa itens inválidos (sem ID de lanche ou bebida) ---
        carrinho = [i for i in carrinho if i.get("id_lanche") or i.get("id_bebida")]

        # Atualiza o carrinho limpo no client_storage
        page.client_storage.set("carrinho", carrinho)

        # --- Verifica se o carrinho está vazio ---
        if not carrinho:
            lv_carrinho.controls.append(
                ft.Text("Seu carrinho está vazio!", color=Colors.RED, size=20, font_family="Arial")
            )
            page.update()
            return

        total = 0.0

        # --- Exibe todos os itens (lanches e bebidas juntos) ---
        for index, item in enumerate(carrinho):
            tipo = item.get("tipo")

            # --- Caso seja um LANCHE ---
            if tipo == "lanche":
                total += float(item.get("valor_lanche", 0))

                lv_carrinho.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Image(src="imagemdolanche.png", height=90),
                                    ft.Column(
                                        [
                                            ft.Text(item.get("nome_lanche", "Lanche"),
                                                    color=Colors.ORANGE_900, size=18, font_family="Arial"),
                                            ft.Text(f'R$ {item.get("valor_lanche", 0):.2f}',
                                                    color=Colors.YELLOW_900,size=17, font_family="Arial"),
                                            ft.Row(
                                                [
                                                    ft.ElevatedButton(
                                                        "Observações",
                                                        on_click=lambda e, idx=index: page.go(
                                                            f"/observacoes/?index={idx}"),
                                                        bgcolor=Colors.ORANGE_700,
                                                        color=Colors.BLACK
                                                    ),
                                                    ft.OutlinedButton(
                                                        "Remover",
                                                        on_click=lambda e, idx=index: remover_item(idx),
                                                        style=ft.ButtonStyle(
                                                            color=Colors.RED_600,
                                                            side=ft.BorderSide(1, Colors.RED_600)
                                                        )
                                                    )
                                                ],
                                                spacing=10
                                            )
                                        ]
                                    )
                                ]
                            ),
                            bgcolor=Colors.BLACK,
                            height=150,
                            border_radius=10,
                            padding=10,
                        ),
                        shadow_color=Colors.YELLOW_900
                    )
                )

            # --- Caso seja uma BEBIDA ---
            elif tipo == "bebida":
                total += float(item.get("valor", 0))

                lv_carrinho.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Image(src="ChatGPT Image 14 de nov. de 2025, 15_44_16.png", height=80),
                                    ft.Column(
                                        [
                                            ft.Text(item.get("nome_bebida", "Bebida"), color=Colors.ORANGE_900, size=18, font_family="Arial"),
                                            ft.Text(f'R$ {item.get("valor", 0):.2f}', color=Colors.YELLOW_900, size=17, font_family="Arial"),
                                            ft.Row(
                                                [
                                                    ft.OutlinedButton(
                                                        "Remover",
                                                        on_click=lambda e, idx=index: remover_item_b(idx),
                                                        style=ft.ButtonStyle(
                                                            color=Colors.RED_600,
                                                            side=ft.BorderSide(1, Colors.RED_600)
                                                        )
                                                    )
                                                ],
                                                spacing=10
                                            )
                                        ]
                                    )
                                ]
                            ),
                            bgcolor=Colors.BLACK,
                            height=150,
                            border_radius=10,
                            padding=10,
                        ),
                        shadow_color=Colors.YELLOW_900
                    )
                )

        # --- Total e botão Finalizar ---
        lv_carrinho.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"Total: R$ {total:.2f}", color=Colors.ORANGE_700, size=20),
                        ft.ElevatedButton(
                            "Finalizar Pedido",
                            on_click=lambda e: page.go("/vendas"),
                            style=ft.ButtonStyle(
                                bgcolor=Colors.ORANGE_700,
                                color=Colors.BLACK,
                                padding=15,
                                shape={"": ft.RoundedRectangleBorder(radius=10)}
                            )
                        )
                    ]
                ),
                padding=20
            )
        )

        page.update()


    def confirmar_pedido_cozinha(e):
        numero_mesa = page.client_storage.get("mesa_atual")

        if numero_mesa is None or numero_mesa == "":
            enviar_pedidos_delivery(page, e)
        else:
            enviar_pedidos_cozinha_garcom(page, e)

    def confirmar_venda(e):
        pessoa_id = page.client_storage.get("pessoa_id")
        if not pessoa_id:
            snack_error("Usuário não logado!")
            page.go("/login")
            return False

        endereco_valor = input_endereco.value.strip()
        if not endereco_valor:
            snack_error("Por favor, informe o endereço!")
            page.update()
            return False

        forma_pagamento_valor = getattr(input_forma_pagamento, "value", None)
        if not forma_pagamento_valor:
            snack_error("Selecione uma forma de pagamento!")
            page.update()
            return False

        # --- pega o carrinho de delivery ---
        carrinho = page.client_storage.get("carrinho") or []
        if isinstance(carrinho, str):
            try:
                carrinho = json.loads(carrinho)
            except:
                carrinho = []

        # --- normaliza ---
        carrinho_normalizado = []
        for it in carrinho:
            item = dict(it)
            item["id_lanche"] = item.get("id_lanche") if item.get("id_lanche") not in [None, ""] else None
            item["id_bebida"] = item.get("id_bebida") if item.get("id_bebida") not in [None, ""] else None

            try:
                if item["id_lanche"] not in [None, ""]:
                    item["id_lanche"] = int(item["id_lanche"])
                if item["id_bebida"] not in [None, ""]:
                    item["id_bebida"] = int(item["id_bebida"])
            except:
                pass

            if "tipo" not in item or not item["tipo"]:
                if item["id_lanche"]:
                    item["tipo"] = "lanche"
                elif item["id_bebida"]:
                    item["tipo"] = "bebida"
                else:
                    item["tipo"] = None

            if item["id_lanche"] or item["id_bebida"]:
                carrinho_normalizado.append(item)
            else:
                print("Ignorado item inválido no carrinho:", it)

        if not carrinho_normalizado:
            snack_error("Nenhum item válido no carrinho!")
            page.update()
            return False

        # --- carrega dados da API ---
        token = page.client_storage.get("token")
        insumos = listar_insumos(token)
        preco_ingredientes = {i["id_insumo"]: i["custo"] for i in insumos}

        # --- valida se lanche/bebida ainda existem ---
        lanches_validos = {l["id_lanche"]: l["nome_lanche"] for l in listar_lanche(token)}
        bebidas_validas = {b["id_bebida"]: b["nome_bebida"] for b in listar_bebidas(token)}

        carrinho_filtrado = []
        for item in carrinho_normalizado:
            if item.get("id_lanche") and item["id_lanche"] not in lanches_validos:
                print(f"Removendo lanche inexistente: {item.get('nome_lanche')}")
                continue
            if item.get("id_bebida") and item["id_bebida"] not in bebidas_validas:
                print(f"Removendo bebida inexistente: {item.get('nome_bebida')}")
                continue
            carrinho_filtrado.append(item)

        carrinho_normalizado = carrinho_filtrado

        if not carrinho_normalizado:
            snack_error("Todos os itens do carrinho foram removidos — produtos inexistentes.")
            page.client_storage.set("carrinho", [])
            page.update()
            return False

        # --- processa os itens válidos ---
        for item in carrinho_normalizado:
            tipo = item.get("tipo")
            id_lanche = item.get("id_lanche")
            id_bebida = item.get("id_bebida")
            qtd = int(item.get("qtd", 1))

            if tipo == "lanche" or id_lanche is not None:
                ingredientes = item.get("ingredientes", {}) or {}
                receita_original = carregar_receita_base(id_lanche) or {}
                observacoes = {"adicionar": [], "remover": []}

                for ing_id, qtd_atual in ingredientes.items():
                    qtd_base = receita_original.get(ing_id, 0)
                    if qtd_atual > qtd_base:
                        observacoes["adicionar"].append({
                            "insumo_id": ing_id,
                            "qtd": qtd_atual - qtd_base,
                            "valor": preco_ingredientes.get(ing_id, 0) * (qtd_atual - qtd_base)
                        })
                    elif qtd_atual < qtd_base:
                        observacoes["remover"].append({
                            "insumo_id": ing_id,
                            "qtd": qtd_base - qtd_atual
                        })

                valor_base = float(item.get("valor_original_lanche", item.get("valor_lanche", 0)))
                valor_extra = sum(obs.get("valor", 0) for obs in observacoes.get("adicionar", []))
                valor_final = (valor_base + valor_extra) * qtd

                detalhamento = f"Lanche: {item.get('nome_lanche', 'Sem nome')} | Obs: {item.get('observacoes_texto', 'Nenhuma')}"

                response = cadastrar_venda_app(
                    lanche_id=id_lanche,
                    pessoa_id=pessoa_id,
                    bebida_id=None,
                    qtd_lanche=qtd,
                    forma_pagamento=forma_pagamento_valor,
                    endereco=endereco_valor,
                    detalhamento=detalhamento,
                    observacoes=observacoes,
                    valor_venda=valor_final
                )

            elif tipo == "bebida" or id_bebida is not None:
                valor_final = float(item.get("valor", 0)) * qtd
                detalhamento = f"Bebida: {item.get('nome_bebida', 'Sem nome')}"

                response = cadastrar_venda_app(
                    lanche_id=None,
                    pessoa_id=pessoa_id,
                    bebida_id=id_bebida,
                    qtd_lanche=qtd,
                    forma_pagamento=forma_pagamento_valor,
                    endereco=endereco_valor,
                    detalhamento=detalhamento,
                    observacoes={},
                    valor_venda=valor_final
                )
            else:
                snack_error(f"Item inválido no carrinho: {item}")
                page.update()
                return False

            if "error" in response:
                snack_error(
                    f"Erro ao cadastrar {item.get('nome_lanche', item.get('nome_bebida', 'item'))}: {response['error']}"
                )
                page.update()
                return False

        # --- limpa campos ---
        input_forma_pagamento.value = ""
        input_endereco.value = ""

        return True

    def confirmar_venda_delivery_e_enviar_cozinha(e):
        try:
            pessoa_id = page.client_storage.get("pessoa_id")
            if not pessoa_id:
                snack_error("Usuário não logado!")
                page.go("/login")
                return

            endereco_valor = input_endereco.value.strip()
            if not endereco_valor:
                snack_error("Informe o endereço!")
                page.update()
                return

            forma_pagamento_valor = getattr(input_forma_pagamento, "value", None)
            if not forma_pagamento_valor:
                snack_error("Selecione uma forma de pagamento!")
                page.update()
                return

            # --- Carrinho ---
            carrinho = page.client_storage.get("carrinho") or []
            if isinstance(carrinho, str):
                try:
                    carrinho = json.loads(carrinho)
                except:
                    carrinho = []

            if not carrinho:
                snack_error("Carrinho vazio!")
                return

            token = page.client_storage.get("token")
            insumos = listar_insumos(token)
            preco_ingredientes = {i["id_insumo"]: i["custo"] for i in insumos}

            # --- REGISTRA VENDA ---
            for item in carrinho:
                id_lanche = item.get("id_lanche")
                id_bebida = item.get("id_bebida")
                qtd = int(item.get("qtd", 1))
                observacoes = {"adicionar": [], "remover": []}
                valor_final = 0

                # LANCHE
                if id_lanche:
                    receita_original = carregar_receita_base(id_lanche) or {}
                    ingredientes_item = item.get("ingredientes", {}) or {}

                    for ing_id, qtd_ajustada in ingredientes_item.items():
                        qtd_base = receita_original.get(ing_id, 0)

                        if qtd_ajustada > qtd_base:
                            extra_qtd = qtd_ajustada - qtd_base
                            observacoes["adicionar"].append({
                                "insumo_id": ing_id,
                                "qtd": extra_qtd,
                                "valor": preco_ingredientes.get(ing_id, 0) * extra_qtd
                            })
                        elif qtd_ajustada < qtd_base:
                            observacoes["remover"].append({
                                "insumo_id": ing_id,
                                "qtd": qtd_base - qtd_ajustada
                            })

                    valor_base = float(item.get("valor_original_lanche", item.get("valor_lanche", 0)))
                    valor_extra = sum(a["valor"] for a in observacoes["adicionar"])
                    valor_final = (valor_base + valor_extra) * qtd

                    detalhamento = f"Lanche: {item.get('nome_lanche')} | Obs: {item.get('observacoes_texto', 'Nenhuma')}"

                    resp = cadastrar_venda_app(
                        lanche_id=id_lanche,
                        pessoa_id=pessoa_id,
                        bebida_id=None,
                        qtd_lanche=qtd,
                        forma_pagamento=forma_pagamento_valor,
                        endereco=endereco_valor,
                        detalhamento=detalhamento,
                        observacoes=observacoes,
                        valor_venda=valor_final
                    )

                # BEBIDA
                elif id_bebida:
                    valor_final = float(item.get("valor", 0)) * qtd
                    detalhamento = f"Bebida: {item.get('nome_bebida')}"

                    resp = cadastrar_venda_app(
                        lanche_id=None,
                        pessoa_id=pessoa_id,
                        bebida_id=id_bebida,
                        qtd_lanche=qtd,
                        forma_pagamento=forma_pagamento_valor,
                        endereco=endereco_valor,
                        detalhamento=detalhamento,
                        observacoes={},
                        valor_venda=valor_final
                    )

                else:
                    snack_error("Item inválido no carrinho!")
                    page.update()
                    return

                if "error" in resp:
                    snack_error(f"Erro ao registrar venda: {resp['error']}")
                    return

            print("Venda registrada com sucesso!")

            #  AGORA SIM — ENVIA PARA COZINHA
            enviar_pedidos_delivery(page, e)

            # SOMENTE AGORA LIMPA O CARRINHO
            page.client_storage.set("carrinho", [])
            input_endereco.value = ""
            input_forma_pagamento.value = ""

            snack_sucesso("Venda realizada e pedido enviado à cozinha!")
            page.go("/")
            page.update()

        except Exception as err:
            print("❌ ERRO EM confirmar_venda_delivery_e_enviar_cozinha:", err)
            snack_error("Erro ao confirmar venda + enviar cozinha.")

    def enviar_pedidos_delivery(page, e):
        id_pessoa = page.client_storage.get("pessoa_id")
        if not id_pessoa:
            snack_error("Usuário não logado!")
            page.go("/login")
            return

        # --- Carrinho delivery ---
        carrinho = page.client_storage.get("carrinho") or []
        if isinstance(carrinho, str):
            try:
                carrinho = json.loads(carrinho)
            except:
                carrinho = []

        if not carrinho:
            snack_error("Nenhum item no carrinho para enviar!")
            page.update()
            return

        # Itens não enviados ainda
        itens_pendentes = [item for item in carrinho if not item.get("enviado")]
        if not itens_pendentes:
            snack_error("Todos os itens desse pedido delivery já foram enviados!")
            page.update()
            return

        # --- Insumos ---
        token = page.client_storage.get("token")
        insumos = listar_insumos(token)
        preco_ingredientes = {i["id_insumo"]: i["custo"] for i in insumos}

        # --- Processa cada item ---
        for item in itens_pendentes:

            id_lanche = item.get("id_lanche")
            id_bebida = item.get("id_bebida")
            qtd = int(item.get("qtd", 1))
            valor_final = 0

            observacoes = {"adicionar": [], "remover": []}

            # ===== LANCHES =====
            if id_lanche:
                receita_original = carregar_receita_base(id_lanche) or {}
                ingredientes_item = item.get("ingredientes", {})

                # Ajuste de ingredientes
                for ing_id, qtd_ajustada in ingredientes_item.items():
                    qtd_base = receita_original.get(ing_id, 0)

                    if qtd_ajustada > qtd_base:
                        observacoes["adicionar"].append({
                            "insumo_id": ing_id,
                            "qtd": qtd_ajustada - qtd_base,
                            "valor": preco_ingredientes.get(ing_id, 0) * (qtd_ajustada - qtd_base)
                        })

                    elif qtd_ajustada < qtd_base:
                        observacoes["remover"].append({
                            "insumo_id": ing_id,
                            "qtd": qtd_base - qtd_ajustada
                        })

                valor_base = float(item.get("valor_original_lanche", item.get("valor_lanche")))
                valor_extra = sum(a["valor"] for a in observacoes["adicionar"])
                valor_final += (valor_base + valor_extra) * qtd

            # ===== BEBIDAS =====
            if id_bebida:
                valor_bebida = float(item.get("valor", 0))
                valor_final += valor_bebida * qtd

            obs_texto = item.get("observacoes_texto", "Nenhuma")

            detalhamento = (
                f"Lanche: {item.get('nome_lanche', '---')} | "
                f"Bebida: {item.get('nome_bebida', '---')} | "
                f"Obs: {obs_texto}"
            )

            # ===== CADASTRA PEDIDO =====
            response = cadastrar_pedido_app(
                id_lanche=id_lanche,
                id_bebida=id_bebida,
                qtd_lanche=qtd,
                detalhamento=detalhamento,
                numero_mesa="",  # DELIVERY NÃO TEM MESA
                observacoes=observacoes,
                id_pessoa=id_pessoa
            )

            if "error" in response:
                snack_error(f"Erro ao cadastrar pedido: {response['error']}")
                return

            # Marca como enviado
            item["enviado"] = True

        # Atualiza carrinho
        page.client_storage.set("carrinho", carrinho)
        snack_sucesso("Pedido realizados com sucesso! \n"
                      "Tempo médio de espera: 1h ")

        page.go("/")
        page.update()

    # FUNÇÕES GARCOM
    def carrinho_view_garcom(page, lv_carrinho_garcom, mesa_num):
        lv_carrinho_garcom.controls.clear()
        print("Atualizando carrinho da mesa:", mesa_num)

        # Recupera carrinhos
        carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}
        carrinho = carrinhos.get(str(mesa_num), [])

        if not carrinho:
            lv_carrinho_garcom.controls.append(
                ft.Text(f"A Mesa {mesa_num} está vazia!", color=Colors.YELLOW_800, size=18)
            )
            page.update()
            return

        # DIVIDE LISTAS
        lanches_mesa = [item for item in carrinho if "nome_lanche" in item]
        bebidas_mesa = [item for item in carrinho if "nome_bebida" in item]

        # CÁLCULO DO TOTAL
        total = sum(
            float(item.get("valor_lanche", 0)) + float(item.get("valor", 0))
            for item in carrinho
        )

        # FUNÇÃO REMOVER (funciona para qualquer item)
        def remover_item(index_real):
            carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}
            carrinho_mesa = carrinhos.get(str(mesa_num), [])

            try:
                item = carrinho_mesa[index_real]

                if item.get("enviado"):
                    snack_error("Este item já foi enviado para a cozinha.")
                    return

                carrinho_mesa.pop(index_real)
                carrinhos[str(mesa_num)] = carrinho_mesa
                page.client_storage.set("carrinhos_por_mesa", carrinhos)

                snack_sucesso("Item removido!")
                carrinho_view_garcom(page, lv_carrinho_garcom, mesa_num)

            except Exception as e:
                snack_error(f"Erro ao remover item: {e}")

        # LISTAR LANCHES
        for item in lanches_mesa:
            index_real = carrinho.index(item)
            enviado = item.get("enviado", False)

            botoes = []
            if not enviado:
                botoes.append(
                    ft.OutlinedButton(
                        "Remover",
                        on_click=lambda e, index=index_real: remover_item(index),
                        style=ft.ButtonStyle(
                            color=Colors.RED_600,
                            side=ft.BorderSide(1, Colors.RED_600)
                        )
                    )
                )

                botoes.append(
                    ft.ElevatedButton(
                        "Observações",
                        on_click=lambda e, item=item: page.go(
                            f"/observacoes_garcom/?id={item['id_lanche']}&mesa={mesa_num}"
                        ),
                        bgcolor=Colors.ORANGE_700,
                        color=Colors.BLACK
                    )
                )

            card_border = Colors.GREEN_400 if enviado else Colors.RED
            status_icon = "✔ Enviado" if enviado else "❌ Pendente"
            status_color = Colors.GREEN_300 if enviado else Colors.RED_400

            lv_carrinho_garcom.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Image(src="imagemdolanche.png", height=80),
                                ft.Column(
                                    [
                                        ft.Text(item["nome_lanche"], color=Colors.ORANGE_900, size=16),
                                        ft.Text(f'R$ {item["valor_lanche"]:.2f}', color=Colors.YELLOW_900),
                                        ft.Text(f"Mesa {mesa_num}", color=Colors.PURPLE_200),
                                        ft.Text(status_icon, color=status_color, size=15, weight=ft.FontWeight.BOLD),
                                        ft.Row(botoes, spacing=10)
                                    ]
                                )
                            ]
                        ),
                        bgcolor=Colors.BLACK,
                        height=180,
                        border_radius=10,
                        padding=10,
                        border=ft.border.all(2, card_border),
                    ),
                    shadow_color=card_border
                )
            )

        # LISTAR BEBIDAS
        for item in bebidas_mesa:
            index_real = carrinho.index(item)
            enviado = item.get("enviado", False)

            botoes = []
            if not enviado:
                botoes.append(
                    ft.OutlinedButton(
                        "Remover",
                        on_click=lambda e, index=index_real: remover_item(index),
                        style=ft.ButtonStyle(
                            color=Colors.RED_600,
                            side=ft.BorderSide(1, Colors.RED_600)
                        )
                    )
                )

            card_border = Colors.GREEN_400 if enviado else Colors.RED
            status_icon = "✔ Enviado" if enviado else "❌ Pendente"
            status_color = Colors.GREEN_300 if enviado else Colors.RED_400

            lv_carrinho_garcom.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Image(src="istockphoto-459361585-170667a.jpg", height=80),
                                ft.Column(
                                    [
                                        ft.Text(item["nome_bebida"], color=Colors.ORANGE_900, size=16),
                                        ft.Text(f'R$ {item["valor"]:.2f}', color=Colors.YELLOW_900),
                                        ft.Text(f"Mesa {mesa_num}", color=Colors.PURPLE_200),
                                        ft.Text(status_icon, color=status_color, size=15, weight=ft.FontWeight.BOLD),
                                        ft.Row(botoes, spacing=10)
                                    ]
                                )
                            ]
                        ),
                        bgcolor=Colors.BLACK,
                        height=180,
                        border_radius=10,
                        padding=10,
                        border=ft.border.all(2, card_border),
                    ),
                    shadow_color=card_border
                )
            )

        # TOTAL + BOTÃO ENVIAR
        lv_carrinho_garcom.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"Total: R$ {total:.2f}", color=Colors.ORANGE_700, size=20),
                        ft.ElevatedButton(
                            "Enviar para cozinha",
                            on_click=lambda e, mesa=mesa_num: confirmar_pedido_cozinha_mesa(e, mesa),
                            style=ft.ButtonStyle(
                                bgcolor=Colors.ORANGE_700,
                                color=Colors.BLACK,
                                padding=15,
                                shape={"": ft.RoundedRectangleBorder(radius=10)}
                            )
                        )
                    ]
                ),
                padding=20
            )
        )

        page.update()

    def enviar_pedidos_cozinha_garcom(page, e):
        id_pessoa = page.client_storage.get("pessoa_id")
        if not id_pessoa:
            snack_error("Garçom não logado!")
            page.go("/login")
            return

        numero_mesa = page.client_storage.get("mesa_atual")
        if not numero_mesa:
            snack_error("Nenhuma mesa selecionada!")
            page.update()
            return

        carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}
        carrinho = carrinhos.get(str(numero_mesa), [])

        if not carrinho:
            snack_error(f"Nenhum item no carrinho da mesa {numero_mesa}!")
            page.update()
            return

        itens_pendentes = [item for item in carrinho if not item.get("enviado")]
        if not itens_pendentes:
            snack_error("Todos os itens dessa mesa já foram enviados!")
            page.update()
            return

        token = page.client_storage.get("token")
        insumos = listar_insumos(token)
        preco_ingredientes = {i["id_insumo"]: i["custo"] for i in insumos}

        for item in itens_pendentes:
            id_lanche = item.get("id_lanche")
            id_bebida = item.get("id_bebida")
            qtd = int(item.get("qtd", 1))
            valor_final = 0

            observacoes = {"adicionar": [], "remover": []}

            # --- Ajuste de ingredientes (lanches)
            if id_lanche:
                receita_original = carregar_receita_base(id_lanche) or {}
                ingredientes_item = item.get("ingredientes", {})

                for ing_id, qtd_ajustada in ingredientes_item.items():
                    qtd_base = receita_original.get(ing_id, 0)

                    if qtd_ajustada > qtd_base:
                        observacoes["adicionar"].append({
                            "insumo_id": ing_id,
                            "qtd": qtd_ajustada - qtd_base,
                            "valor": preco_ingredientes.get(ing_id, 0) * (qtd_ajustada - qtd_base)
                        })
                    elif qtd_ajustada < qtd_base:
                        observacoes["remover"].append({
                            "insumo_id": ing_id,
                            "qtd": qtd_base - qtd_ajustada
                        })

                valor_base = float(item.get("valor_original_lanche", item.get("valor_lanche")))
                valor_extra = sum(a["valor"] for a in observacoes["adicionar"])
                valor_final += (valor_base + valor_extra) * qtd

            # --- Bebidas
            if id_bebida:
                valor_bebida = float(item.get("valor", 0))
                valor_final += valor_bebida * qtd

            obs_texto = item.get("observacoes_texto", "Nenhuma")

            detalhamento = (
                f"Lanche: {item.get('nome_lanche', '---')} | "
                f"Bebida: {item.get('nome_bebida', '---')} | "
                f"Obs: {obs_texto}"
            )

            response = cadastrar_pedido_app(
                id_lanche=id_lanche,
                id_bebida=id_bebida,
                qtd_lanche=qtd,
                detalhamento=detalhamento,
                numero_mesa=numero_mesa,
                observacoes=observacoes,
                id_pessoa=id_pessoa
            )

            if "error" in response:
                snack_error(f"Erro ao cadastrar pedido: {response['error']}")
                return

            item["enviado"] = True

        carrinhos[str(numero_mesa)] = carrinho
        page.client_storage.set("carrinhos_por_mesa", carrinhos)

        snack_sucesso(f"Pedidos da mesa {numero_mesa} enviados!")
        page.update()

        page.go("/mesa")
        page.update()


    # apenas injeta o número da mesa
    def confirmar_pedido_cozinha_mesa(e, mesa_num):
        page.client_storage.set("mesa_atual", mesa_num)
        confirmar_pedido_cozinha(e)

    def confirmar_venda_garcom(e):
        pessoa_id = page.client_storage.get("pessoa_id")
        if not pessoa_id:
            snack_error("Garçom não logado!")
            page.go("/login")
            return

        # Pegamos a mesa da rota atual
        query = urlparse(page.route).query
        params = parse_qs(query)
        mesa_num = params.get("mesa", [""])[0]

        # Recupera o carrinho dessa mesa
        carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}
        carrinho = carrinhos.get(str(mesa_num), [])

        if not carrinho:
            snack_error(f"Nenhum item no carrinho da Mesa {mesa_num}!")
            page.update()
            return

        # Forma de pagamento
        forma_pagamento_valor = getattr(input_forma_pagamento, "value", None)
        if not forma_pagamento_valor:
            snack_error("Selecione uma forma de pagamento!")
            page.update()
            return

        endereco = "Presencial"

        # Busca insumos
        token = page.client_storage.get("token")
        insumos = listar_insumos(token)
        preco_ingredientes = {i["id_insumo"]: i["custo"] for i in insumos}

        for item in carrinho:
            id_lanche = item.get("id_lanche")
            id_bebida = item.get("id_bebida")
            qtd_lanche = int(item.get("qtd", 1))

            observacoes = {"adicionar": [], "remover": []}
            valor_final = 0.0
            detalhamento = ""



            # === Lanche ===
            if id_lanche:
                ingredientes = item.get("ingredientes", {})
                receita_original = carregar_receita_base(id_lanche)

                for ing_id, qtd in ingredientes.items():
                    qtd_base = receita_original.get(ing_id, 0)
                    if qtd > qtd_base:
                        observacoes["adicionar"].append({
                            "insumo_id": ing_id,
                            "qtd": qtd - qtd_base,
                            "valor": preco_ingredientes.get(ing_id, 0) * (qtd - qtd_base)
                        })
                    elif qtd < qtd_base:
                        observacoes["remover"].append({
                            "insumo_id": ing_id,
                            "qtd": qtd_base - qtd
                        })

                valor_base = float(item.get("valor_original_lanche", item.get("valor_lanche", 0)))
                valor_extra = sum(obs.get("valor", 0) for obs in observacoes.get("adicionar", []))
                valor_final = (valor_base + valor_extra) * qtd_lanche

                detalhamento = f"Lanche: {item.get('nome_lanche', 'Sem nome')} | Obs: {item.get('observacoes_texto', 'Nenhuma')}"

            # === Bebida ===
            elif id_bebida:
                valor_final = float(item.get("valor", 0)) * qtd_lanche
                detalhamento = f"Bebida: {item.get('nome_bebida', 'Sem nome')}"

            else:
                snack_error("Item inválido no carrinho (sem lanche nem bebida).")
                continue

            # === Cadastra venda ===
            response = cadastrar_venda_app(
                lanche_id=id_lanche if id_lanche else None,
                pessoa_id=pessoa_id,
                bebida_id=id_bebida if id_bebida else None,
                qtd_lanche=qtd_lanche,
                forma_pagamento=forma_pagamento_valor,
                endereco=endereco,
                detalhamento=detalhamento,
                observacoes=observacoes if id_lanche else {},
                valor_venda=valor_final
            )

            if "error" in response:
                snack_error(f"Erro ao cadastrar item: {response['error']}")
                page.update()
                return

        # === Limpa somente a mesa atual ===
        carrinhos.pop(str(mesa_num), None)
        page.client_storage.set("carrinhos_por_mesa", carrinhos)

        snack_sucesso(f"Venda da Mesa {mesa_num} registrada com sucesso!")
        page.go("/mesa")
        page.update()

        # ----------------------------

    def salvar_carrinho(e):
        mesa_valor = numero_mesa.value.strip()
        lanche_id = lanche_dropdown.value
        bebida_id = bebidas_dropdow.value

        if not mesa_valor:
            snack_error("Informe o número da mesa antes de salvar.")
            page.update()
            return

        if not lanche_id and not bebida_id:
            snack_error("Selecione pelo menos um lanche ou uma bebida.")
            page.update()
            return

        # Carrinhos por mesa
        carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}
        carrinho_mesa = carrinhos.get(str(mesa_valor), [])

        if lanche_id:
            lanche = next((l for l in lanches_disponiveis if l["id_lanche"] == int(lanche_id)), None)
            carrinho_mesa.append({
                "id_lanche": lanche["id_lanche"],
                "nome_lanche": lanche["nome_lanche"],
                "valor_lanche": lanche["valor_lanche"],
                "mesa": mesa_valor,
                "enviado": False
            })

        if bebida_id:
            bebida = next((b for b in bebidas_disponiveis if b["id_bebida"] == int(bebida_id)), None)
            carrinho_mesa.append({
                "id_bebida": bebida["id_bebida"],
                "nome_bebida": bebida["nome_bebida"],
                "valor": bebida["valor"],
                "mesa": mesa_valor,
                "enviado": False
            })

        carrinhos[str(mesa_valor)] = carrinho_mesa
        page.client_storage.set("carrinhos_por_mesa", carrinhos)

        page.client_storage.set("mesa_atual", mesa_valor)

        snack_sucesso(f"Pedido da Mesa {mesa_valor} adicionado com sucesso!")

        # Limpa valores internos
        numero_mesa.value = ""
        lanche_dropdown.value = None
        bebidas_dropdow.value = None

        # Remove foco


        # Atualiza mesas abertas
        mesa_dropdown_aberta.options = [
            ft.dropdown.Option(m, f"Mesa {m}") for m in listar_mesas_abertas()
        ]

        # PRIMEIRO volta para rota mesa
        page.go("/mesa")

        # DEPOIS atualiza
        page.update()

    def listar_mesas_abertas():
        # Busca o dicionário completo de carrinhos
        carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}

        # Filtra apenas mesas com pelo menos 1 item
        mesas_abertas = [mesa for mesa, itens in carrinhos.items() if itens]

        # Retorna em ordem numérica (pra não virar string bagunçada)
        try:
            mesas_abertas = sorted(mesas_abertas, key=lambda m: int(m))
        except:
            mesas_abertas = sorted(mesas_abertas)

        return mesas_abertas

    # ***************************************************************************/*******************************





    # 🔔 Modal de Confirmação (Pedido Presencial)
    def fechar_dialogo(e):
        dlg_modal.open = False
        page.update()
        print("✅ Pedido confirmado!")  # Aqui pode chamar cadastrar_vendas()

    dlg_modal = ft.AlertDialog(
        title=ft.Text("ALERTA‼️", color=Colors.BLACK),
        content=ft.Text(
            "Chame o Garçom mais próximo e faça seu pedido\n"
            "Após cadastrado não terá como editar.\n"
            "Então se quiser realizar mudanças, já faça suas observações ao garçom 😁.\n",

            color=Colors.WHITE,
            font_family='Arial',
            size=18
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo(e)),
            ft.TextButton("OK ✅", on_click=lambda e: fechar_dialogo(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=Colors.ORANGE_800,
    )

    # *****************************//*************************************

    # Rotas
    def gerencia_rotas(e):
        page.views.clear()
        # page.padding = 0
        page.views.append(
            View(
                "/",
                [

                    ft.Container(
                        width=page.window.width,
                        height=page.window.height,
                        image=ft.DecorationImage(
                            src="imagem1.png", fit=ft.ImageFit.COVER
                        )
                    ),

                ], bgcolor=Colors.BLACK, floating_action_button=usuario,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, vertical_alignment=ft.MainAxisAlignment.CENTER
            )
        )

        if page.route == "/login":
            page.views.append(
                View(
                    "/login",
                    [
                        AppBar(title=logo, center_title=True, bgcolor=Colors.BLACK, color=Colors.PURPLE, title_spacing=5
                               ),
                        ft.Container(
                            width=page.window.width,
                            height=page.window.height,
                            image=ft.DecorationImage(
                                src="fundo.jpg", opacity=0.8
                            ),

                            content=ft.Column([
                                input_email,
                                input_senha,
                                btn_login,
                                btn_cadastro_login,
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

                        ),
                    ], bgcolor=Colors.BLACK, horizontal_alignment=ft.CrossAxisAlignment.CENTER, padding=11,
                    vertical_alignment=ft.MainAxisAlignment.CENTER
                )
            )

        if page.route == "/cadastrar_pessoa":
            input_email.value = ""
            input_senha.value = ""
            page.views.append(
                View(
                    "/cadastrar_pessoa",
                    [
                        AppBar(title=Text('Cadastro', color=Colors.YELLOW_900),
                               title_text_style=TextStyle(weight=ft.FontWeight.BOLD, font_family="Playfair Display",
                                                          size=18), leading=fundo, bgcolor=Colors.BLACK,
                               center_title=True),
                        input_nome,
                        input_email_cadastrado,
                        input_senha_cadastro,
                        # input_cpf,
                        # input_papel_user,
                        # input_status_user_usuario,

                        # slider_salario,

                        # txt_salario,

                        ElevatedButton(
                            "Cadastrar",
                            on_click=lambda e: cadastro_click_user(e),
                            bgcolor=Colors.ORANGE_800,
                            color=Colors.BLACK,
                        ),
                        ElevatedButton(
                            "Voltar",
                            on_click=lambda e: page.go("/login"),
                            bgcolor=Colors.ORANGE_800,
                            color=Colors.BLACK,
                        ),
                    ], bgcolor=Colors.BLACK

                )
            )

        if page.route == "/mesa":
            # numero_mesa.value = ""
            # lanche_dropdown.value = ""
            # bebidas_dropdow.value = ""
            # Containers, ícones e botões
            icone_mesa = ft.Icon(ft.Icons.TABLE_RESTAURANT, color=Colors.ORANGE_800, size=30)
            icone_lanche = ft.Icon(ft.Icons.FASTFOOD, color=Colors.ORANGE_800, size=30)
            icone_bebida = ft.Icon(ft.Icons.LOCAL_DRINK, color=Colors.ORANGE_800, size=30)

            btn_salvar_carrinho = ft.ElevatedButton("Adicionar Pedido", on_click=salvar_carrinho,
                                                    bgcolor=Colors.ORANGE_700, color=Colors.BLACK,)

            page.views.append(
                ft.View(
                    "/mesa",
                    [
                        ft.AppBar(
                            title=ft.Image(src="imgdois.png", width=90),
                            center_title=True,
                            bgcolor=Colors.BLACK,
                            color=Colors.PURPLE,
                            leading=logo,
                            actions=[btn_logout]
                        ),
                        ft.Column([
                            ft.Row([icone_mesa, numero_mesa], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([icone_lanche, lanche_dropdown], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([icone_bebida, bebidas_dropdow], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([btn_salvar_carrinho], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Divider(height=20, color=Colors.PURPLE),
                            ft.Text("Mesas Abertas", size=20, color=Colors.BLACK),
                            ft.Row([mesa_dropdown_aberta], alignment=ft.MainAxisAlignment.CENTER),
                        ], )
                    ],
                    bgcolor=Colors.ORANGE_100
                )
            )
            page.update()

        # Carrinho Garçom
        if page.route.startswith("/carrinho_garcom"):
            print("carrinho garcom")

            query = urlparse(page.route).query
            params = parse_qs(query)
            mesa_num = params.get("mesa", [""])[0]  # pega o valor após ?mesa=

            if not mesa_num:
                snack_error("Número da mesa não informado!")
                page.go("/mesa")
                return


            lv_carrinho_garcom = ft.ListView(expand=True, spacing=10, padding=10)
            carrinho_view_garcom(page, lv_carrinho_garcom, mesa_num)

            # ---------------- BOTÕES ----------------

            btn_voltar = ft.ElevatedButton(
                "Voltar para Mesas",
                on_click=lambda e: page.go("/mesa"),
                style=ft.ButtonStyle(bgcolor=Colors.BLACK, color=Colors.WHITE, padding=15)
            )

            def tentar_fechar_mesa(e, mesa=mesa_num):
                token = page.client_storage.get("token")

                if not token:
                    snack_error("Garçom não logado!")
                    page.go("/login")
                    return

                # --- Carrinho local da mesa ---
                carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}
                carrinho_da_mesa = carrinhos.get(str(mesa), [])


                # --- Verifica itens pendentes (não enviados para cozinha) ---
                itens_pendentes = [item for item in carrinho_da_mesa if not item.get("enviado")]

                if itens_pendentes:
                    snack_error("Há itens dessa mesa ainda não enviados para a cozinha!")
                    page.update()
                    return

                if not carrinho_da_mesa:
                    snack_error(f"A mesa {mesa} não possui itens no carrinho.")
                    page.update()
                    return

                # Todos enviados
                snack_sucesso(f"Mesa {mesa} pronta para fechamento!")
                page.go(f"/vendas_garcom?mesa={mesa}")
                page.update()

            btn_fechar_mesa = ft.ElevatedButton(
                "Fechar Mesa",
                on_click=lambda e, mesa=mesa_num: tentar_fechar_mesa(e, mesa),
                style=ft.ButtonStyle(bgcolor=Colors.ORANGE_700, color=Colors.BLACK, padding=15)
            )

            page.views.append(
                ft.View(
                    "/carrinho_garcom",
                    [
                        ft.AppBar(
                            title=ft.Text(f"Carrinho da Mesa {mesa_num}", color=Colors.ORANGE_700),
                            center_title=True,
                            bgcolor=Colors.BLACK,
                        ),
                        lv_carrinho_garcom,

                        btn_voltar,
                        btn_fechar_mesa,

                    ],
                    bgcolor=Colors.ORANGE_100,
                )
            )

            page.update()

        # Rota observação Garçom, igual o delivery
        if page.route.startswith("/observacoes_garcom"):
            print("observacoes_garcom")

            def get_lanche_por_id():
                query = urlparse(page.route).query
                params = parse_qs(query)
                return params.get("id", [None])[0]

            def carregar_carrinho_item(lanche_id):
                """
                Retorna o item do carrinho correspondente ao id_lanche para mesas do garçom.
                """
                try:
                    lanche_id = int(lanche_id)
                except (ValueError, TypeError):
                    return None

                numero_mesa = page.client_storage.get("mesa_atual")
                if not numero_mesa:
                    return None

                carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}
                carrinho = carrinhos.get(str(numero_mesa), [])

                for item in carrinho:
                    if item.get("id_lanche") == lanche_id:
                        return item

                return None

            def carregar_insumos_disponiveis(token):
                insumos = [i for i in listar_insumos(token) if i.get("qtd_insumo", 0) > 5]
                return (
                    {i["id_insumo"]: i["nome_insumo"] for i in insumos},  # nomes
                    {i["id_insumo"]: i["custo"] for i in insumos}  # preços
                )

            # ==========================
            # Inicialização
            # ==========================
            lanche_id = get_lanche_por_id()
            item = carregar_carrinho_item(lanche_id)
            token = page.client_storage.get("token")

            if not item:
                page.views.append(
                    ft.View(
                        "/erro",
                        [ft.Text("Lanche não encontrado!", color=Colors.RED_700, size=22)]
                    )
                )
                page.update()
                return

            ingredientes_disponiveis, preco_ingredientes = carregar_insumos_disponiveis(token)
            valor_base_original = item.get("valor_original_lanche", item.get("valor_lanche", 0))
            item["valor_original_lanche"] = valor_base_original

            lanche_id = item.get("id_lanche")
            receita_original = carregar_receita_base(lanche_id) if lanche_id else {}

            # Mantém alterações salvas ou receita original
            ingredientes_salvos = item.get("ingredientes") or {}
            item["ingredientes"] = {
                ing_id: ingredientes_salvos.get(ing_id, receita_original.get(ing_id, 0))
                for ing_id in ingredientes_disponiveis
            }

            # ==========================
            # UI e Funções de Controle
            # ==========================
            ingrediente_controls = {}
            preco_label = ft.Text(f"Preço total: R$ {valor_base_original:.2f}", color=Colors.ORANGE_900, size=18)
            MAX_ADICIONAIS = 3

            def atualizar_preco():
                total = valor_base_original
                detalhes = []
                for ing_id, txt in ingrediente_controls.items():
                    qtd_atual = int(txt.value)
                    qtd_base = receita_original.get(ing_id, 0)
                    diff = qtd_atual - qtd_base
                    if diff > 0:
                        preco_unit = preco_ingredientes.get(ing_id, 0)
                        total += diff * preco_unit
                        detalhes.append(
                            f"{ingredientes_disponiveis[ing_id]}: +{diff} x R$ {preco_unit:.2f} = R$ {diff * preco_unit:.2f}"
                        )
                preco_label.value = f"Preço total: R$ {total:.2f}\n" + ("\n".join(detalhes) if detalhes else "")
                page.update()
                return total

            def make_alterar_func(ing_id, qtd_base):
                def aumentar(e):
                    qtd = int(ingrediente_controls[ing_id].value)
                    if qtd < MAX_ADICIONAIS + qtd_base:
                        ingrediente_controls[ing_id].value = str(qtd + 1)
                        atualizar_preco()
                    else:
                        page.snack_bar = ft.SnackBar(
                            ft.Text("Limite Máximo atingido!"),
                            open=True, bgcolor=Colors.RED_700, duration=1500
                        )
                        page.update()

                def diminuir(e):
                    qtd = int(ingrediente_controls[ing_id].value)
                    if qtd > 0:
                        ingrediente_controls[ing_id].value = str(qtd - 1)
                        atualizar_preco()

                return aumentar, diminuir

            # Monta controles visuais
            controles_lista = []
            for ing_id, qtd in item["ingredientes"].items():
                if ing_id in ingredientes_disponiveis:
                    nome = ingredientes_disponiveis[ing_id]
                    txt = ft.Text(str(qtd), color=Colors.WHITE, size=18, weight="bold")
                    ingrediente_controls[ing_id] = txt
                    qtd_base = receita_original.get(ing_id, 0)
                    aumentar, diminuir = make_alterar_func(ing_id, qtd_base)

                    controles_lista.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(f"{nome} (R$ {preco_ingredientes[ing_id]:.2f})",
                                                color=Colors.ORANGE_900, size=16, weight="bold"),
                                        ft.Row(
                                            [
                                                ft.IconButton(ft.Icons.REMOVE_ROUNDED, icon_color=Colors.RED_700,
                                                              on_click=diminuir),
                                                txt,
                                                ft.IconButton(ft.Icons.ADD_ROUNDED, icon_color=Colors.GREEN_700,
                                                              on_click=aumentar)
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER, spacing=10
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                padding=10, bgcolor=Colors.ORANGE_100, border_radius=10,
                                alignment=ft.alignment.center
                            ),
                            elevation=3, shadow_color=Colors.YELLOW_800
                        )
                    )

            obs_input = ft.TextField(
                label="Detalhes do lanche",
                hint_text='Ex: Ponto da Carne',
                value=item.get("observacoes_texto", ""),
                color=Colors.ORANGE_900, multiline=True, width=350,
                border_color=Colors.ORANGE_700, border_radius=10,
                content_padding=10, bgcolor=Colors.WHITE
            )

            def salvar_observacoes(e):

                # --- pega todos carrinhos ---
                carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}
                mesa = str(item["mesa"])
                carrinho = carrinhos.get(mesa, [])

                # --- recalcula quantidades ---
                valores_atualizados = {ing_id: int(txt.value) for ing_id, txt in ingrediente_controls.items()}

                observacoes = {"adicionar": [], "remover": []}

                for ing_id, qtd_base in receita_original.items():
                    qtd_nova = valores_atualizados.get(ing_id, 0)
                    if qtd_nova > qtd_base:
                        observacoes["adicionar"].append({"insumo_id": ing_id, "qtd": qtd_nova - qtd_base})
                    elif qtd_nova < qtd_base:
                        observacoes["remover"].append({"insumo_id": ing_id, "qtd": qtd_base - qtd_nova})

                for ing_id, qtd_nova in valores_atualizados.items():
                    if ing_id not in receita_original and qtd_nova > 0:
                        observacoes["adicionar"].append({"insumo_id": ing_id, "qtd": qtd_nova})

                novo_valor = atualizar_preco()

                # --- salva no carrinho da mesa correta ---
                for i, it in enumerate(carrinho):
                    if it.get("id_lanche") == lanche_id:
                        carrinho[i].update({
                            "observacoes_texto": obs_input.value or "Nenhuma",
                            "ingredientes": valores_atualizados,
                            "valor_lanche": novo_valor,
                            "valor_venda": novo_valor,
                            "observacoes": observacoes
                        })
                        break

                #  agora salvando no lugar correto!
                carrinhos[mesa] = carrinho
                page.client_storage.set("carrinhos_por_mesa", carrinhos)

                snack_sucesso("Observações salvas com sucesso!")
                page.update()
                page.go(f"/carrinho_garcom?mesa={mesa}")

            atualizar_preco()

            # ==========================
            # Montagem da view
            # ==========================
            page.views.append(
                ft.View(
                    "/observacoes_garcom",
                    [
                        ft.AppBar(
                            title=ft.Text("Personalizar Lanche", size=22, color=Colors.ORANGE_900, weight="bold"),
                            center_title=True, bgcolor=Colors.BLACK, actions=[btn_logout_observacoes_garcom]
                        ),
                        ft.Column([
                            ft.Text(f"Editando: {item['nome_lanche']}", color=Colors.YELLOW_800, size=22,
                                    weight="bold"),
                            ft.GridView(controles_lista, max_extent=150, spacing=15, run_spacing=15, padding=10),
                            obs_input,
                            preco_label,
                            ft.Row([
                                ft.ElevatedButton("Salvar", on_click=salvar_observacoes, bgcolor=Colors.GREEN_700,
                                                  color=Colors.WHITE),
                                ft.OutlinedButton("Cancelar",
                                                  on_click=lambda e: page.go(
                                                      f"/carrinho_garcom?mesa={item['mesa']}"))
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=25, expand=True, scroll=True)
                    ],
                    bgcolor=Colors.ORANGE_50
                )
            )
            page.update()


        if page.route.startswith("/vendas_garcom"):
            query = urlparse(page.route).query
            params = parse_qs(query)
            mesa_num = params.get("mesa", [""])[0]

            input_forma_pagamento.value = ""
            input_endereco.value = ""

            # Recupera o carrinho da mesa atual
            carrinhos = page.client_storage.get("carrinhos_por_mesa") or {}
            carrinho_mesa = carrinhos.get(str(mesa_num), [])

            if not carrinho_mesa:
                snack_error(f"Nenhum pedido encontrado na Mesa {mesa_num}.")
                page.go("/mesa")
                return

            # === Monta resumo de itens ===
            resumo_itens = []
            for item in carrinho_mesa:
                nome_lanche = item.get("nome_lanche")
                nome_bebida = item.get("nome_bebida")

                # Se o item tem lanche
                if nome_lanche:
                    resumo_itens.append(
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text(f"🍔 {nome_lanche}", color=Colors.ORANGE_900, size=16),
                                    ft.Text(f"R$ {float(item.get('valor_lanche', 0)):.2f}", color=Colors.YELLOW_800,
                                            size=16),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=ft.padding.symmetric(vertical=4),
                        )
                    )

                # Se o item tem bebida
                if nome_bebida:
                    resumo_itens.append(
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text(f"🍹{nome_bebida}", color=Colors.BLUE_900, size=16),
                                    ft.Text(f"R$ {float(item.get('valor', 0)):.2f}", color=Colors.YELLOW_800, size=16),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=ft.padding.symmetric(vertical=4),
                        )
                    )

            # === Total ===
            total = sum(float(item.get("valor_lanche", 0)) + float(item.get("valor", 0)) for item in carrinho_mesa)

            total_label = ft.Text(
                f"💵 Total da Mesa {mesa_num}: R$ {total:.2f}",
                color=Colors.ORANGE_700,
                size=20,
                weight=ft.FontWeight.BOLD
            )

            # === Botões ===
            btn_fechar_venda = ft.ElevatedButton(
                "Confirmar Venda",
                bgcolor=Colors.ORANGE_700,
                color=Colors.BLACK,
                on_click=lambda e: confirmar_venda_garcom(e)
            )

            btn_voltar = ft.ElevatedButton(
                "Voltar",
                bgcolor=Colors.ORANGE_100,
                color=Colors.BLACK,
                on_click=lambda e: page.go(f"/carrinho_garcom?mesa={mesa_dropdown_aberta.value}")
            )

            # === Monta tela ===
            page.views.append(
                ft.View(
                    "/vendas_garcom",
                    [
                        ft.AppBar(
                            title=ft.Text(f"Fechamento - Mesa {mesa_num}", color=Colors.ORANGE_700),
                            center_title=True,
                            bgcolor=Colors.BLACK,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Resumo do Pedido:", color=Colors.BLACK, size=18,
                                            weight=ft.FontWeight.BOLD),
                                    *resumo_itens,
                                    ft.Divider(thickness=1, color=Colors.GREY_700),
                                    total_label,
                                    ft.Divider(thickness=1, color=Colors.GREY_700),
                                    input_forma_pagamento,
                                    ft.Row(
                                        [btn_fechar_venda, btn_voltar],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=20
                                    ),
                                ],
                                spacing=10,
                                scroll=ft.ScrollMode.AUTO
                            ),
                            padding=20,
                            bgcolor=Colors.YELLOW_100,
                        ),
                    ],
                    bgcolor=Colors.YELLOW_100,
                )
            )

            page.update()

        if page.route == "/presencial_delivery":
            page.views.append(
                ft.View(
                    "/presencial_delivery",
                    appbar=ft.AppBar(
                        bgcolor=Colors.BLACK,
                        actions=[btn_logout],
                    ),
                    controls=[
                        ft.Container(
                            expand=True,
                            image=ft.DecorationImage(
                                src="fundo.jpg",
                                fit=ft.ImageFit.COVER
                            ),
                            content=ft.Column(
                                [
                                    ft.Container(
                                        expand=True,
                                        alignment=ft.alignment.center,
                                        content=ft.Column(
                                            [
                                                ft.ElevatedButton(
                                                    "Presencial",
                                                    on_click=lambda _: page.go("/cardapio_presencial"),
                                                    style=ft.ButtonStyle(
                                                        shape={"": ft.RoundedRectangleBorder(radius=15)},
                                                        padding=20,
                                                        bgcolor=Colors.ORANGE_600,

                                                        color=Colors.BLACK,

                                                    ),
                                                ),
                                                ft.ElevatedButton(
                                                    "Delivery",
                                                    on_click=lambda _: page.go("/cardapio_delivery"),
                                                    style=ft.ButtonStyle(
                                                        shape={"": ft.RoundedRectangleBorder(radius=15)},
                                                        padding=20,
                                                        bgcolor=Colors.BLACK,
                                                        color=Colors.ORANGE_400,

                                                    ),
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=30,
                                        ),
                                    ),
                                ],
                                spacing=0,
                            ),
                        ),
                    ],
                    bgcolor="#000000000",
                )
            )

        if page.route == "/cardapio_presencial":
            cardapio_bebidas(e)
            cardapio(e)
            page.views.append(
                View(
                    "/cardapio",
                    [
                        AppBar(
                            title=ft.Text(
                                "CARDÁPIO",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=Colors.WHITE,
                            ),
                            leading=ft.Image(src="imgdois.png", width=60),
                            center_title=True,
                            bgcolor=Colors.BLACK,


                            actions=[btn_logout_cardapio],
                            title_spacing=0,
                        ),
                        t
                    ],
                    bgcolor=Colors.ORANGE_800,
                )
            )

        if page.route == "/cardapio_delivery":
            cardapio_delivery(e)
            cardapio_delivery_bebida(e)

            page.views.append(
                View(
                    "/cardapio",
                    [
                        AppBar(
                            title=ft.Text(
                                "CARDÁPIO",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=Colors.WHITE,
                            ),
                            leading=ft.Image(src="imgdois.png", width=60),
                            center_title=True,
                            bgcolor=Colors.BLACK,

                            actions=[btn_logout_cardapio],
                            title_spacing=0,
                        ),
                        t
                    ],
                    bgcolor=Colors.ORANGE_800,
                )
            )

        if page.route == "/carrinho":
            carrinho_view(e)
            page.views.append(
                View(
                    "/carrinho",
                    [
                        AppBar(title=ft.Image(src="imgdois.png", width=90), center_title=True, bgcolor=Colors.BLACK,
                               color=Colors.PURPLE, title_spacing=5, leading=logo, actions=[btn_logout_carrinho]),

                        lv_carrinho,

                    ],
                    bgcolor=Colors.BLACK,
                )

            )

        if page.route.startswith("/observacoes/"):
            print("observacoes")
            print("CARRINHO AO ENTRAR NA ROTA:", page.client_storage.get("carrinho"))

            # ==========================
            # Funções auxiliares
            # ==========================
            def get_lanche_index():
                query = urlparse(page.route).query
                params = parse_qs(query)
                try:
                    return int(params.get("index", [-1])[0])
                except ValueError:
                    return -1

            def carregar_carrinho_item(index):
                carrinho = page.client_storage.get("carrinho") or []
                if 0 <= index < len(carrinho):
                    return carrinho[index]
                return {"nome_lanche": "Lanche não encontrado", "valor_lanche": 0, "ingredientes": {}}

            def carregar_insumos_disponiveis(token):
                insumos = [i for i in listar_insumos(token) if i.get("qtd_insumo", 0) > 5]
                return (
                    {i["id_insumo"]: i["nome_insumo"] for i in insumos},  # nomes
                    {i["id_insumo"]: i["custo"] for i in insumos}  # preços
                )

            # ==========================
            # Inicialização
            # ==========================
            lanche_index = get_lanche_index()
            item = carregar_carrinho_item(lanche_index)
            token = page.client_storage.get("token")
            ingredientes_disponiveis, preco_ingredientes = carregar_insumos_disponiveis(token)

            valor_base_carrinho = item.get("valor_original_lanche", item.get("valor_lanche", 0))
            item["valor_original_lanche"] = valor_base_carrinho

            lanche_id = item.get("id_lanche")
            receita_original = carregar_receita_base(lanche_id) if lanche_id else {}

            lanches = listar_lanche(token)
            print("lanches: ", lanches)
            for lanche in lanches:
                if lanche_id == lanche["id_lanche"]:
                    valor_base_original = lanche["valor_lanche"]

            # Mantém alterações salvas ou receita original
            ingredientes_salvos_raw = item.get("ingredientes") or {}
            ingredientes_salvos = {int(k): v for k, v in ingredientes_salvos_raw.items()}
            item["ingredientes"] = {ing_id: ingredientes_salvos.get(ing_id, receita_original.get(ing_id, 0))
                                    for ing_id in ingredientes_disponiveis}

            # ==========================
            # UI e funções de controle
            # ==========================
            ingrediente_controls = {}
            preco_label = ft.Text(f"Preço total: R$ {valor_base_carrinho:.2f}", color=Colors.ORANGE_900, size=18)
            MAX_ADICIONAIS = 3

            def atualizar_preco():
                total = valor_base_original
                detalhes = []
                for ing_id, txt in ingrediente_controls.items():
                    qtd_atual = int(txt.value)
                    qtd_base = receita_original.get(ing_id, 0)
                    diff = qtd_atual - qtd_base
                    if diff > 0:
                        preco_unit = preco_ingredientes.get(ing_id, 0)
                        total += diff * preco_unit
                        detalhes.append(
                            f"{ingredientes_disponiveis[ing_id]}: +{diff} x R$ {preco_unit:.2f} = R$ {diff * preco_unit:.2f}")
                preco_label.value = f"Preço total: R$ {total:.2f}\n" + "\n".join(detalhes)
                page.update()
                return total

            def make_alterar_func(ing_id, qtd_base):
                def aumentar(e):
                    qtd = int(ingrediente_controls[ing_id].value)
                    if qtd < MAX_ADICIONAIS + qtd_base:
                        ingrediente_controls[ing_id].value = str(qtd + 1)
                        atualizar_preco()
                    else:
                        page.snack_bar = ft.SnackBar(
                            ft.Text("Limite Máximo atingido!"),
                            open=True, bgcolor=Colors.RED_700, duration=1500
                        )
                        page.update()

                def diminuir(e):
                    qtd = int(ingrediente_controls[ing_id].value)
                    if qtd > 0:
                        ingrediente_controls[ing_id].value = str(qtd - 1)
                        atualizar_preco()

                return aumentar, diminuir

            # Monta controles visuais
            controles_lista = []
            for ing_id, qtd in item["ingredientes"].items():
                if ing_id in ingredientes_disponiveis:
                    nome = ingredientes_disponiveis[ing_id]
                    txt = ft.Text(str(qtd), color=Colors.WHITE, size=18, weight="bold")
                    ingrediente_controls[ing_id] = txt
                    qtd_base = receita_original.get(ing_id, 0)
                    aumentar, diminuir = make_alterar_func(ing_id, qtd_base)

                    controles_lista.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(f"{nome} (R$ {preco_ingredientes[ing_id]:.2f})",
                                                color=Colors.ORANGE_900, size=16, weight="bold"),
                                        ft.Row([ft.IconButton(ft.Icons.REMOVE_ROUNDED, icon_color=Colors.RED_700,
                                                              on_click=diminuir),
                                                txt,
                                                ft.IconButton(ft.Icons.ADD_ROUNDED, icon_color=Colors.GREEN_700,
                                                              on_click=aumentar)],
                                               alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                padding=10, bgcolor=Colors.ORANGE_100, border_radius=10, alignment=ft.alignment.center
                            ),
                            elevation=3, shadow_color=Colors.YELLOW_800
                        )
                    )

            obs_input = ft.TextField(
                label="Detalhes do lanche",
                hint_text='Ex: Ponto da Carne',
                value=item.get("observacoes_texto", ""),
                color=Colors.ORANGE_900, multiline=True, width=350,
                border_color=Colors.ORANGE_700, border_radius=10,
                content_padding=10, bgcolor=Colors.WHITE
            )

            def salvar_observacoes(e):
                carrinho = page.client_storage.get("carrinho") or []
                if 0 <= lanche_index < len(carrinho):
                    item_copy = carrinho[lanche_index].copy()

                    valores_atualizados = {
                        ing_id: int(txt.value or 0)
                        for ing_id, txt in ingrediente_controls.items()
                    }

                    observacoes = {"adicionar": [], "remover": []}
                    for ing_id, qtd_base in receita_original.items():
                        qtd_nova = valores_atualizados.get(ing_id, 0)
                        if qtd_nova > qtd_base:
                            observacoes["adicionar"].append({"insumo_id": ing_id, "qtd": qtd_nova - qtd_base})
                        elif qtd_nova < qtd_base:
                            observacoes["remover"].append({"insumo_id": ing_id, "qtd": qtd_base - qtd_nova})

                    for ing_id, qtd_nova in valores_atualizados.items():
                        if ing_id not in receita_original and qtd_nova > 0:
                            observacoes["adicionar"].append({"insumo_id": ing_id, "qtd": qtd_nova})

                    preco_total = atualizar_preco()

                    print("ANTES DE SALVAR:", ingredientes_salvos)
                    print("RECEITA ORIGINAL:", receita_original)
                    print("INGREDIENTES SALVOS:", valores_atualizados)

                    # diferença entre o que ficou salvo e a receita original
                    diferenca = {
                        k: valores_atualizados.get(k, 0) - receita_original.get(k, 0)
                        for k in valores_atualizados
                    }

                    adicionados = []
                    removidos = []

                    for ing_id, qtd_atual in valores_atualizados.items():
                        qtd_base = receita_original.get(ing_id, 0)
                        nome = ingredientes_disponiveis.get(ing_id, f"ID {ing_id}")

                        diff = qtd_atual - qtd_base

                        if diff > 0:
                            # aumentou = ingrediente adicionado
                            adicionados.append(f"{nome} (+{diff * 100}g)")

                        elif diff < 0:
                            # diminuiu = ingrediente removido
                            removidos.append(f"{nome} (-{abs(diff) * 100}g)")

                    print("REMOVIDOS:", removidos)
                    print("ADICIONADOS:", adicionados)

                    page.client_storage.set("adicionados", adicionados)
                    page.client_storage.set("removidos", removidos)

                    item_copy.update({
                        "observacoes_texto": obs_input.value or "Nenhuma",
                        "ingredientes": valores_atualizados,
                        "valor_lanche": preco_total,
                        "valor_venda": preco_total,
                        "observacoes": observacoes
                    })
                    carrinho[lanche_index] = item_copy
                    page.client_storage.set("carrinho", carrinho)

                    snack_sucesso("Observações salvas com sucesso!")
                    page.update()
                    # page.snack_bar = ft.SnackBar(
                    #     ft.Text(),
                    #     open=True, bgcolor=Colors.GREEN_700, duration=1500
                    # )
                    page.update()
                page.go("/carrinho")

            # ==========================
            # Montagem da view
            # ==========================
            page.views.append(
                ft.View(
                    "/observacoes",
                    [
                        ft.AppBar(title=ft.Text("Personalizar Lanche", size=22, color=Colors.ORANGE_900, weight="bold"),
                                  center_title=True, bgcolor=Colors.BLACK, actions=[btn_logout_observacoes]),
                        ft.Column([
                            ft.Text(f"Você está editando: {item['nome_lanche']}", color=Colors.YELLOW_800, size=22,
                                    weight="bold"),
                            ft.GridView(controles_lista, max_extent=150, spacing=15, run_spacing=15, padding=10),
                            obs_input,
                            preco_label,
                            ft.Row([
                                ft.ElevatedButton("Salvar", on_click=salvar_observacoes, bgcolor=Colors.GREEN_700,
                                                  color=Colors.WHITE),
                                ft.OutlinedButton("Cancelar", on_click=lambda e: page.go("/carrinho"))
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=25, expand=True, scroll=True)
                    ],
                    bgcolor=Colors.ORANGE_50
                )
            )
            page.update()

        if page.route == "/vendas":
            #  Limpa o histórico de views antigas
            page.views.clear()

            # --- Recupera carrinho ---
            carrinho = page.client_storage.get("carrinho") or []

            # Garante que é sempre uma lista
            if isinstance(carrinho, str):
                try:
                    carrinho = json.loads(carrinho)
                except:
                    carrinho = []

            if not carrinho:
                snack_error("Carrinho vazio! Adicione itens antes de finalizar.")
                page.go("/carrinho")
                return

            # Campo de endereço + opção de retirada
            def atualizar_endereco(e):
                if seletor_entrega.value == "retirada":
                    input_endereco.value = "Retirada no balcão"
                    input_endereco.disabled = True
                else:
                    input_endereco.value = ""
                    input_endereco.disabled = False
                page.update()

            seletor_entrega = ft.Dropdown(
                width=300,
                label="Forma de Entrega",
                options=[
                    ft.dropdown.Option("endereco"),
                    ft.dropdown.Option("retirada"),
                ],
                value="endereco",
                on_change=atualizar_endereco,
            )



            # --- Filtra por tipo ---
            lanches = [i for i in carrinho if i.get("tipo") == "lanche"]
            bebidas = [i for i in carrinho if i.get("tipo") == "bebida"]

            #  Carrega insumos
            token = page.client_storage.get("token")
            insumos = listar_insumos(token)
            ingredientes_disponiveis = {i["id_insumo"]: i["nome_insumo"] for i in insumos}

            lista_itens = []
            lista_itens_bebida = []
            total = 0.0

            # --- Lanches ---
            for item in lanches:
                total += item.get("valor_lanche", 0)
                obs_texto = item.get("observacoes_texto", "Nenhuma")


                adicionados = page.client_storage.get("adicionados")
                removidos = page.client_storage.get("removidos")

                lista_itens.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(item.get("nome_lanche", "Lanche"), color=Colors.ORANGE_700, size=16),
                                ft.Text(f"R$ {item['valor_lanche']:.2f}", color=Colors.YELLOW_900, size=14),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"Obs: {obs_texto}", color=Colors.YELLOW_800, size=12),
                            ft.Text("Adicionados: " + (", ".join(adicionados) if adicionados else "Nenhum"),
                                    color=Colors.GREEN_700, size=12),
                            ft.Text("Removidos: " + (", ".join(removidos) if removidos else "Nenhum"),
                                    color=Colors.RED_700, size=12),
                        ]),
                        padding=15,
                        bgcolor=Colors.BLACK,
                        border_radius=10,
                    )
                )

            # --- Bebidas ---
            for item in bebidas:
                total += item.get("valor", 0)
                lista_itens_bebida.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(item.get("nome_bebida", "Bebida"), color=Colors.ORANGE_700, size=16),
                                ft.Text(f"R$ {item['valor']:.2f}", color=Colors.YELLOW_900, size=14),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ]),
                        padding=15,
                        bgcolor=Colors.BLACK,
                        border_radius=10,
                    )
                )

            total_label = ft.Text(f"Total do Pedido: R$ {total:.2f}", color=Colors.ORANGE_700, size=20)

            # --- Exibe tela ---
            page.views.append(
                ft.View(
                    "/vendas",
                    [
                        ft.AppBar(
                            title=ft.Image(src="imgdois.png", width=90),
                            center_title=True,
                            bgcolor=Colors.BLACK,
                            leading=logo,
                            actions=[btn_logout_carrinho],
                        ),
                        ft.Column(
                            [
                                ft.Text("Resumo do Pedido", size=22, color=Colors.BLACK, font_family="Arial"),
                                ft.Column([
                                    ft.ListView(controls=lista_itens, expand=True),
                                    ft.ListView(controls=lista_itens_bebida, expand=True),
                                    total_label,

                                    seletor_entrega,
                                    input_endereco,

                                    input_forma_pagamento,
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                text="Confirmar Venda",
                                                bgcolor=Colors.ORANGE_800,
                                                color=Colors.BLACK,
                                                on_click=confirmar_venda_delivery_e_enviar_cozinha
,

                                            ),
                                            ft.OutlinedButton(
                                                "Voltar",
                                                on_click=lambda e: page.go("/carrinho"),
                                            ),

                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=20,
                                    )
                                ]),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                            expand=True,
                            scroll=True,
                        ),
                    ],
                    bgcolor=Colors.ORANGE_100,
                )
            )

        page.update()



    # Componentes
    loading_indicator = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

    lv_lanches = ft.ListView(expand=True)
    lv_carrinho = ft.ListView(expand=True)

    lv_bebidas = ft.ListView(expand=True)
    lv_porcoes = ft.ListView(expand=True)

    input_email = ft.TextField(
        label="Email",
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800, border_radius=5,
    )

    input_endereco = ft.TextField(label="Endereço de Entrega", width=300, color=Colors.ORANGE_700)

    input_senha = ft.TextField(
        label="Senha",
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        password=True,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800, border_radius=5,
        can_reveal_password=True
    )

    input_nome = ft.TextField(
        label="Insira seu nome",
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800
    )

    input_email_cadastrado = ft.TextField(
        hint_text='Insira seu email',
        col=4,
        width=300,
        label="Email",
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800
    )

    input_senha_cadastro = ft.TextField(
        hint_text='Insira sua senha',
        col=4,
        width=300,
        label="Senha",
        password=True,
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800
    )

    input_status_user = ft.Dropdown(
        label="Status",
        width=300, bgcolor=Colors.ORANGE_800,
        fill_color=Colors.ORANGE_800, color=Colors.ORANGE_800, text_style=TextStyle(color=Colors.WHITE),
        options=[
            Option(key="Ativo", text="Ativo"),
            Option(key="Inativo", text="Inativo"),

        ]
    )

    input_forma_pagamento = ft.Dropdown(
        label="Forma de pagamento",
        width=300, bgcolor=Colors.ORANGE_800,
        fill_color=Colors.ORANGE_800, color=Colors.DEEP_ORANGE_800, text_style=TextStyle(color=Colors.BLACK),
        options=[
            Option(key="Dinheiro", text="Dinheiro"),
            Option(key="Credito", text="Crédito"),
            Option(key="Debito", text="Débito"),
            Option(key="Pix", text="Pix"),

        ]

    )

    # Indicador de carregamento
    loading_indicator = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

    # Botões Login
    btn_cadastro_login = ft.ElevatedButton(
        text="Cadastrar",
        icon=Icons.LOGIN,
        bgcolor=Colors.ORANGE_800,
        color=Colors.BLACK,
        width=page.window.width,
        height=30,
        icon_color=Colors.WHITE,
        on_click=lambda _: page.go('/cadastrar_pessoa'),

    )

    btn_login = ft.ElevatedButton(
        text="Logar",
        icon=Icons.VERIFIED_USER,
        bgcolor=Colors.ORANGE_800,
        color=Colors.BLACK,
        width=page.window.width,
        height=30,
        icon_color=Colors.WHITE,
        on_click=click_login,

    )

    # Imagens
    logo = ft.Image(
        src="fundo.jpg",  # troque para o caminho da sua imagem local ou URL
        fit=ft.ImageFit.CONTAIN,
        width=80, opacity=0.9,

    )

    fundo = ft.GestureDetector(
        on_tap=lambda e: page.go("/"),  # substitua "/inicio" pela rota que quiser
        content=ft.Image(
            src="fundo.jpg",  # troque para o caminho da sua imagem local ou URL
            fit=ft.ImageFit.CONTAIN
        )
    )

    usuario = ft.TextButton(icon=Icons.LOGIN, text="Entrar", icon_color=Colors.RED_700,
                            on_click=lambda _: page.go('/login'))

    # Botoões Logout
    btn_logout = ft.TextButton(
        icon=Icons.LOGOUT,
        scale=1.5,
        icon_color=Colors.RED_700,
        on_click=click_logout
    )

    btn_logout_cardapio = ft.TextButton(
        icon=Icons.LOGOUT,
        scale=1.5,
        icon_color=Colors.RED_700,
        on_click=lambda  _: page.go('/presencial_delivery')
    )

    btn_logout_observacoes = ft.TextButton(
        icon=Icons.LOGOUT,
        scale=1.5,
        icon_color=Colors.RED_700,
        on_click=lambda _: page.go('/cardapio_delivery'),
    )

    btn_logout_observacoes_garcom = ft.TextButton(
        icon=Icons.LOGOUT,
        scale=1.5,
        icon_color=Colors.RED_700,
        on_click=lambda _: page.go(f"/carrinho_garcom?mesa={mesa_dropdown_aberta.value}")
    )

    btn_logout_carrinho = ft.TextButton(
        icon=Icons.LOGOUT,
        scale=1.5,
        icon_color=Colors.RED_700,
        on_click=lambda _: page.go("/cardapio_delivery"),
    )

    btn_logout_carrinho_garcom = ft.TextButton(
        icon=Icons.LOGOUT,
        scale=1.5,
        icon_color=Colors.RED_700,
        on_click=lambda _: page.go('/mesa'),
    )

    # Pessoas
    input_cpf = ft.TextField(
        label='Cpf',
        hint_text='insira cpf',
        col=4,
        bgcolor=Colors.RED_900,
        color=Colors.BLACK,
        opacity=0.9,
        fill_color=Colors.ORANGE_800,
        label_style=TextStyle(color=ft.Colors.WHITE),
        border_color=Colors.DEEP_PURPLE_800

    )

    input_papel = ft.Dropdown(

        label="Papel",
        width=300, bgcolor=Colors.ORANGE_800,
        fill_color=Colors.ORANGE_800, color=Colors.ORANGE_800, text_style=TextStyle(color=Colors.WHITE),
        options=[
            Option(key="Cliente", text="Cliente"),
            Option(key="garcom", text="Garçom"),

        ]
    )

    # Cardápios
    # t = ft.Tabs(
    #
    #     selected_index=1,
    #     animation_duration=300,
    #
    #     tabs=[
    #
    #         ft.Tab(
    #             text="Bebidas",
    #             icon=ft.Icons.LOCAL_DRINK,
    #             content=ft.Container(
    #                 lv_bebidas,
    #             ),
    #         ),
    #
    #         ft.Tab(
    #             text="Lanches",
    #             icon=ft.Icons.FOOD_BANK,
    #             content=ft.Container(
    #                 lv_lanches,
    #
    #             ),
    #         ),
    #     ],
    #     expand=1,
    # )

    t = ft.Tabs(
        selected_index=1,
        animation_duration=300,
        indicator_color=Colors.AMBER,
        divider_color="transparent",
        label_color=Colors.WHITE,
        unselected_label_color=Colors.WHITE,
        scrollable=False,

        tabs=[
            ft.Tab(
                text="Bebidas",
                icon=ft.Icons.LOCAL_DRINK,
                content=ft.Container(
                    lv_bebidas,
                    padding=20,
                    border_radius=20,
                    bgcolor=Colors.BLACK,
                    shadow=ft.BoxShadow(
                        blur_radius=18,
                        spread_radius=2,
                        color=ft.Colors.with_opacity(0.25, Colors.BLACK),

                    ),
                    margin=ft.margin.all(12),
                ),
            ),

            ft.Tab(
                text="Lanches",
                icon=ft.Icons.FASTFOOD,
                content=ft.Container(
                    lv_lanches,
                    padding=20,
                    border_radius=20,
                    bgcolor=Colors.BLACK,
                    shadow=ft.BoxShadow(
                        blur_radius=18,
                        spread_radius=2,
                        color=ft.Colors.with_opacity(0.25, Colors.BLACK),

                    ),
                    margin=ft.margin.all(12),
                ),
            ),
        ],
        expand=1,
    )

    # GARÇOM
    lanches_disponiveis = listar_lanche(token)
    bebidas_disponiveis = listar_bebidas(token)
    clientes_disponiveis = listar_pessoas()  # lista de cadastrados
    mesas_disponiveis = listar_mesas_abertas()

    numero_mesa = ft.TextField(
        label="Número da Mesa",
        hint_text="Ex: 5",
        width=180,
        border_color=Colors.PURPLE,
        color=Colors.BLACK,
        # bgcolor=Colors.DEEP_ORANGE_100
    )

    lanches_ordenados = sorted(
        [l for l in lanches_disponiveis if l.get("disponivel") == True],
        key=lambda x: x["nome_lanche"].lower()
    )

    lanche_dropdown = ft.Dropdown(
        label="Selecione o Lanche",
        width=250,
        border_color=Colors.PURPLE,
        color=Colors.BLACK,
        bgcolor=Colors.DEEP_ORANGE_100,
        options=[
            ft.dropdown.Option(str(l["id_lanche"]), l["nome_lanche"])
            for l in lanches_ordenados
        ]
    )

    bebidas_ordenadas = sorted(
        bebidas_disponiveis,
        key=lambda x: x["nome_bebida"].lower()
    )

    bebidas_dropdow = ft.Dropdown(
        label="Selecione a bebida",
        width=250,
        border_color=Colors.PURPLE,
        color=Colors.BLACK,
        bgcolor=Colors.DEEP_ORANGE_100,
        options=[
            ft.dropdown.Option(str(b["id_bebida"]), b["nome_bebida"])
            for b in bebidas_ordenadas
        ]
    )



    cliente_dropdown = ft.Dropdown(
        label="Selecione o Cliente",
        width=250,
        border_color=Colors.PURPLE,
        color=Colors.BLACK,
        bgcolor=Colors.DEEP_ORANGE_100,
        options=[ft.dropdown.Option(str(c["id_pessoa"]), c["nome_pessoa"]) for c in clientes_disponiveis]
    )

    # mesa_dropdown_aberta = ft.Dropdown(
    #     label="Mesas Abertas",
    #     width=200,
    #     bgcolor=Colors.DEEP_ORANGE_100,
    #     options=[ft.dropdown.Option(m, f"Mesa {m}") for m in mesas_disponiveis],
    #     on_change=lambda e: page.go(f"/carrinho_garcom?mesa={mesa_dropdown_aberta.value}")
    # )

    mesa_dropdown_aberta = ft.Dropdown(
        label="Mesas Abertas",
        width=200,
        bgcolor=Colors.DEEP_ORANGE_100,
        options=[ft.dropdown.Option(m, f"Mesa {m}") for m in mesas_disponiveis],
        on_change=lambda e: page.go(f"/carrinho_garcom?mesa={mesa_dropdown_aberta.value}")
    )

    # Componentes não utlizados, mas necessários para o cadastrar pessoas
    slider_salario = ft.Slider(min=0, max=50000, divisions=485, label="{value}",
                               active_color=Colors.ORANGE_800,
                               inactive_color=Colors.ORANGE_900, on_change=display_slider_salario,
                               thumb_color=Colors.RED
                               )

    txt_salario = ft.Text(value='SALÁRIO: 0', font_family="Consolas", size=18, color=Colors.WHITE, animate_size=20,
                          weight=FontWeight.BOLD, theme_style=TextThemeStyle.HEADLINE_SMALL)

    # Eventos
    page.on_route_change = gerencia_rotas
    page.on_close = page.client_storage.remove("auth_token")
    page.go(page.route)


# Comando que executa o aplicativo
# Deve estar sempre colado na linha
ft.app(main)