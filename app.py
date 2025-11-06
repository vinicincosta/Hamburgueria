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


        token = page.client_storage.get('token')
        resultado_bebidas = listar_bebidas(token)

        print(f'Resultado das bebidas: {resultado_bebidas}')

        for bebida in resultado_bebidas:
            # Mostra só os ativos
                lv_bebidas.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Image(src="istockphoto-459361585-170667a.jpg", height=100),
                                    ft.Column(
                                        [
                                            ft.Text(f'{bebida["nome_bebida"]}', color=Colors.ORANGE_900),
                                            ft.Text(f'R$ {bebida["valor"]:.2f}', color=Colors.YELLOW_900),
                                            ft.Text(f'{bebida["descricao"]}',
                                                    color=Colors.YELLOW_800, width=200),
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
                                            ft.Text(f'{lanche["nome_lanche"]}', color=Colors.ORANGE_900),
                                            ft.Text(f'R$ {lanche["valor_lanche"]:.2f}', color=Colors.YELLOW_900),
                                            ft.Text(f'{lanche["descricao_lanche"]}',
                                                    color=Colors.YELLOW_800, width=200),
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

        # def adicionar_ao_carrinho(lanche):
        #     carrinho = page.client_storage.get("carrinho")
        #     carrinho.append(lanche)
        #     page.client_storage.set("carrinho", carrinho)
        #
        #     # Mensagem de sucesso
        #     snack_sucesso(f"{lanche['nome_lanche']} adicionado ao carrinho!")
        #     page.update()
        #     print(f"Carrinho atualizado: {carrinho}")

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
                                    ft.Image(src="imagemdolanche.png", height=100),
                                    ft.Column(
                                        [
                                            ft.Text(f'{lanche["nome_lanche"]}', color=Colors.ORANGE_900),
                                            ft.Text(f'R$ {lanche["valor_lanche"]:.2f}', color=Colors.YELLOW_900),

                                            ft.Text(f'{lanche["descricao_lanche"]}',
                                                    color=Colors.YELLOW_800, width=200, font_family="Aharoni"),



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
        lv_bebidas.controls.clear()  # limpa antes de carregar

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
                lv_bebidas.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Image(src="istockphoto-459361585-170667a.jpg", height=100),
                                    ft.Column(
                                        [
                                            ft.Text(f'{bebida["nome_bebida"]}', color=Colors.ORANGE_900),
                                            ft.Text(f'R$ {bebida["valor"]:.2f}', color=Colors.YELLOW_900),

                                            ft.Text(f'{bebida["descricao"]}',
                                                    color=Colors.YELLOW_800, width=200, font_family="Aharoni"),

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

                # Total + botão finalizar



    #Função para remover item do carrinho
    def remover_item(index):
        carrinho = page.client_storage.get("carrinho") or []
        if 0 <= index < len(carrinho):
            # pop é usado para remover e retornar

            item_removido = carrinho.pop(index)  # remove o item
            page.client_storage.set("carrinho", carrinho)
            snack_sucesso(f"{item_removido['nome_lanche']} removido do carrinho!")
            carrinho_view(None)  # recarrega a tela

    #
    def remover_item_b(index):
        carrinho = page.client_storage.get("carrinho") or []
        if 0 <= index < len(carrinho):
            # pop é usado para remover e retornar

            item_removido = carrinho.pop(index)  # remove o item
            page.client_storage.set("carrinho", carrinho)
            snack_sucesso(f"{item_removido['nome_bebida']} removido do carrinho!")
            carrinho_view(None)  # recarrega a tela

    def carrinho_view(e):
        lv_carrinho.controls.clear()

        # Garante que o carrinho é sempre uma lista válida
        carrinho = page.client_storage.get("carrinho") or []
        if isinstance(carrinho, str):
            try:
                carrinho = json.loads(carrinho)
            except:
                carrinho = []

        if not carrinho:
            lv_carrinho.controls.append(
                ft.Text("Seu carrinho está vazio!", color=Colors.YELLOW_800, size=18)
            )
        else:
            total = 0.0

            # --- Exibe LANCHES ---
            for index, item in enumerate(carrinho):
                if item.get("tipo") == "lanche":
                    total += float(item.get("valor_lanche", 0))

                    lv_carrinho.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Image(src="imagemdolanche.png", height=80),
                                        ft.Column(
                                            [
                                                ft.Text(item.get("nome_lanche", "Lanche"), color=Colors.ORANGE_900,
                                                        size=16),
                                                ft.Text(f'R$ {item.get("valor_lanche", 0):.2f}',
                                                        color=Colors.YELLOW_900),
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

            # --- Exibe BEBIDAS ---
            for index, item in enumerate(carrinho):
                if item.get("tipo") == "bebida":
                    total += float(item.get("valor", 0))

                    lv_carrinho.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Image(src="istockphoto-459361585-170667a.jpg", height=80),
                                        ft.Column(
                                            [
                                                ft.Text(item.get("nome_bebida", "Bebida"), color=Colors.ORANGE_900),
                                                ft.Text(f'R$ {item.get("valor", 0):.2f}', color=Colors.YELLOW_900),
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

        id_pessoa = page.client_storage.get("pessoa_id")
        if not id_pessoa:
            snack_error("Garcom não logado!")
            page.go("/login")
            return

        # Usa o carrinho correto (garçom)
        carrinho = page.client_storage.get("carrinho_garcom") or []
        if not carrinho:
            snack_error("Nenhum item no carrinho da mesa!")
            page.update()
            return



        token = page.client_storage.get("token")
        insumos = listar_insumos(token)
        preco_ingredientes = {i["id_insumo"]: i["custo"] for i in insumos}

        # Pega número da mesa do primeiro item (todos têm o mesmo)
        numero_mesa = carrinho[0].get("mesa")

        for item in carrinho:
            id_lanche = item.get("id_lanche")
            id_bebida = page.client_storage.get("id_bebida")
            qtd_lanche = int(item.get("qtd", 1))
            ingredientes = item.get("ingredientes", {})

            # Receita base do lanche
            receita_original = carregar_receita_base(id_lanche)
            observacoes = {"adicionar": [], "remover": []}

            # Verifica modificações
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
                        "qtd": qtd_base - qtd # apenas registro, não desconta do preço
                    })

            # Calcula valor final do lanche
            valor_base = float(item.get("valor_original_lanche", item.get("valor_lanche", 0)))
            valor_extra = sum(obs.get("valor", 0) for obs in observacoes.get("adicionar", []))
            valor_final = (valor_base + valor_extra) * qtd_lanche

            # Atualiza item
            item.update({
                "valor_venda": valor_final,
                "valor_lanche": valor_final,
                "observacoes": observacoes
            })

            obs_texto = str(item.get("observacoes_texto", "Nenhuma"))
            detalhamento = f"Lanche: {item.get('nome_lanche', 'Sem nome')} | Obs: {obs_texto}"

            # Chama API para cadastrar pedido
            response = cadastrar_pedido_app(
                id_lanche=id_lanche,
                id_bebida=id_bebida,
                qtd_lanche=qtd_lanche,
                detalhamento=detalhamento,
                observacoes=observacoes,
                numero_mesa=numero_mesa,
                id_pessoa=id_pessoa

            )

        # Verifica resposta
            if "error" in response:
                snack_error(f"Erro ao cadastrar {item.get('nome_lanche', 'lanche')}: {response['error']}")
                page.update()
                return

        # Limpa o carrinho da mesa e confirma sucesso
        page.client_storage.set("carrinho_garcom", [])
        snack_sucesso("Pedido enviado para a cozinha com sucesso!")
        page.go("/mesa")
        page.update()


    def confirmar_venda(e):
        pessoa_id = page.client_storage.get("pessoa_id")
        if not pessoa_id:
            snack_error("Usuário não logado!")
            page.go("/login")
            return

        endereco_valor = input_endereco.value.strip()
        if not endereco_valor:
            snack_error("Por favor, informe o endereço!")
            page.update()
            return

        forma_pagamento_valor = getattr(input_forma_pagamento, "value", None)
        if not forma_pagamento_valor:
            snack_error("Selecione uma forma de pagamento!")
            page.update()
            return

        carrinho = page.client_storage.get("carrinho") or []
        if not carrinho:
            snack_error("Seu carrinho está vazio!")
            page.update()
            return

        token = page.client_storage.get("token")
        insumos = listar_insumos(token)

        # Tabela fixa de preços
        preco_ingredientes = {i["id_insumo"]: i["custo"] for i in insumos}

        for item in carrinho:
            id_lanche = item.get("id_lanche")
            id_bebida = item.get("id_bebida")
            qtd_lanche = item.get("qtd", 1)
            ingredientes = item.get("ingredientes", {})

            # Recupera receita base do lanche
            receita_original = carregar_receita_base(id_lanche)
            observacoes = {"adicionar": [], "remover": []}

            # Verifica modificações
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
                        "qtd": qtd_base - qtd  # apenas registro, não desconta do preço
                    })

            # Recalcula valor do lanche considerando apenas os extras
            valor_base = float(item.get("valor_original_lanche", item.get("valor_lanche", 0)))
            valor_extra = sum(obs.get("valor", 0) for obs in observacoes.get("adicionar", []))
            valor_final = (valor_base + valor_extra) * qtd_lanche

            # Atualiza item no carrinho
            item["valor_venda"] = valor_final
            item["valor_lanche"] = valor_final
            item["observacoes"] = observacoes

            obs_texto = item.get("observacoes_texto", "Nenhuma")
            detalhamento = f"Lanche: {item.get('nome_lanche', 'Sem nome')} | Obs: {obs_texto}"

            # Chama a API para cadastrar venda
            response = cadastrar_venda_app(
                lanche_id=id_lanche,
                pessoa_id=pessoa_id,
                bebida_id=id_bebida,
                qtd_lanche=qtd_lanche,
                forma_pagamento=forma_pagamento_valor,
                endereco=endereco_valor,
                detalhamento=detalhamento,
                observacoes=observacoes,
                valor_venda=valor_final
            )

            if "error" in response:
                snack_error(f"Erro ao cadastrar {item.get('nome_lanche', 'lanche')}: {response['error']}")
                page.update()
                return

        # Limpa carrinho após confirmação
        page.client_storage.set("carrinho", [])
        snack_sucesso("Pedido confirmado! Seu lanche chegará em até 1 hora.")
        page.go("/")
        page.update()

    # Funções Garçom
    def carrinho_view_garcom(page, lv_carrinho_garcom, mesa_num):
        lv_carrinho_garcom.controls.clear()
        print("Atualizando carrinho da mesa:", mesa_num)

        # Pega carrinho salvo
        carrinho = page.client_storage.get("carrinho_garcom") or []

        # Garante IDs únicos e normaliza mesa
        for item in carrinho:
            # Gera ID apenas conforme o tipo do item
            if "nome_lanche" in item and "id_lanche" not in item:
                item["id_lanche"] = str(uuid.uuid4())

            if "nome_bebida" in item and "id_bebida" not in item:
                item["id_bebida"] = str(uuid.uuid4())

            item["mesa"] = str(item.get("mesa", "")).strip()

        # Filtra itens apenas da mesa atual
        carrinho_mesa = [item for item in carrinho if item["mesa"] == mesa_num]

        # Separa os itens por tipo
        lanches_mesa = [item for item in carrinho_mesa if "nome_lanche" in item]
        bebidas_mesa = [item for item in carrinho_mesa if "nome_bebida" in item]

        if not carrinho_mesa:
            lv_carrinho_garcom.controls.append(
                ft.Text(f"A Mesa {mesa_num} está vazia!", color=Colors.YELLOW_800, size=18)
            )
        else:
            # Calcula total (lanche + bebida)
            total = sum(
                float(item.get("valor_lanche", 0)) + float(item.get("valor", 0))
                for item in carrinho_mesa
            )

            # === Funções de remover ===
            def remover_item(id_lanche):
                carrinho = page.client_storage.get("carrinho_garcom") or []
                carrinho = [item for item in carrinho if item.get("id_lanche") != id_lanche]
                page.client_storage.set("carrinho_garcom", carrinho)
                snack_sucesso("Lanche removido do carrinho!")
                carrinho_view_garcom(page, lv_carrinho_garcom, mesa_num)

            def remover_item_b(id_bebida):
                carrinho = page.client_storage.get("carrinho_garcom") or []
                carrinho = [item for item in carrinho if item.get("id_bebida") != id_bebida]
                page.client_storage.set("carrinho_garcom", carrinho)
                snack_sucesso("Bebida removida do carrinho!")
                carrinho_view_garcom(page, lv_carrinho_garcom, mesa_num)

            # === Lanches ===
            for item in lanches_mesa:
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
                                            ft.Text(f"Mesa {item['mesa']}", color=Colors.PURPLE_200),
                                            ft.Row(
                                                [
                                                    ft.OutlinedButton(
                                                        "Remover",
                                                        on_click=lambda e, id_lanche=item["id_lanche"]: remover_item(
                                                            id_lanche),
                                                        style=ft.ButtonStyle(
                                                            color=Colors.RED_600,
                                                            side=ft.BorderSide(1, Colors.RED_600)
                                                        )
                                                    ),
                                                    ft.ElevatedButton(
                                                        "Observações",
                                                        on_click=lambda e, item=item: page.go(
                                                            f"/observacoes_garcom/?id={item['id_lanche']}"
                                                        ),
                                                        bgcolor=Colors.ORANGE_700,
                                                        color=Colors.BLACK
                                                    ),
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

            # === Bebidas ===
            for item in bebidas_mesa:
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
                                            ft.Text(f"Mesa {item['mesa']}", color=Colors.PURPLE_200),
                                            ft.Row(
                                                [
                                                    ft.OutlinedButton(
                                                        "Remover",
                                                        on_click=lambda e, id_bebida=item["id_bebida"]: remover_item_b(
                                                            id_bebida),
                                                        style=ft.ButtonStyle(
                                                            color=Colors.RED_600,
                                                            side=ft.BorderSide(1, Colors.RED_600)
                                                        )
                                                    ),
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

            # === Total e botão ===
            lv_carrinho_garcom.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"Total: R$ {total:.2f}", color=Colors.ORANGE_700, size=20),
                            ft.ElevatedButton(
                                "Enviar para cozinha",
                                on_click=lambda e: confirmar_pedido_cozinha(e),
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

    def confirmar_venda_garcom(e):
        pessoa_id = page.client_storage.get("pessoa_id")
        if not pessoa_id:
            snack_error("Garçom não logado!")
            page.go("/login")
            return

        # Carrinho do garçom (vinculado à mesa)
        carrinho = page.client_storage.get("carrinho_garcom") or []


        # Forma de pagamento
        forma_pagamento_valor = getattr(input_forma_pagamento, "value", None)
        if not forma_pagamento_valor:
            snack_error("Selecione uma forma de pagamento!")
            page.update()
            return

        # Endereço fixo: venda presencial
        endereco = "Presencial"

        # Busca insumos para calcular preços extras
        token = page.client_storage.get("token")
        insumos = listar_insumos(token)
        preco_ingredientes = {i["id_insumo"]: i["custo"] for i in insumos}

        for item in carrinho:
            id_lanche = item.get("id_lanche")
            id_bebida = item.get("id_bebida")
            qtd_lanche = item.get("qtd", 1)
            ingredientes = item.get("ingredientes", {})

            # Receita original do lanche
            receita_original = carregar_receita_base(id_lanche)
            observacoes = {"adicionar": [], "remover": []}

            # Verifica modificações feitas no lanche
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

            # Calcula o valor final (base + extras)
            valor_base = float(item.get("valor_original_lanche", item.get("valor_lanche", 0)))
            valor_extra = sum(obs.get("valor", 0) for obs in observacoes.get("adicionar", []))
            valor_final = (valor_base + valor_extra) * qtd_lanche

            # Atualiza item
            item["valor_venda"] = valor_final
            item["valor_lanche"] = valor_final
            item["observacoes"] = observacoes

            obs_texto = item.get("observacoes_texto", "Nenhuma")
            detalhamento = f"Lanche: {item.get('nome_lanche', 'Sem nome')} | Obs: {obs_texto}"

            # Chama API para registrar a venda
            response = cadastrar_venda_app(
                lanche_id=id_lanche,
                pessoa_id=pessoa_id,
                bebida_id=id_bebida,
                qtd_lanche=qtd_lanche,
                forma_pagamento=forma_pagamento_valor,
                endereco=endereco,  # sempre "Presencial"
                detalhamento=detalhamento,
                observacoes=observacoes,
                valor_venda=valor_final
            )

            if "error" in response:
                snack_error(f"Erro ao cadastrar {item.get('nome_lanche', 'lanche')}: {response['error']}")
                page.update()
                return

        # Limpa carrinho após confirmação
        page.client_storage.set("carrinho_garcom", [])
        snack_sucesso("Pedido confirmado! Venda presencial registrada com sucesso.")
        page.go("/vendas_garcom")
        page.update()

        # ----------------------------

    def salvar_carrinho(e):
        mesa_valor = numero_mesa.value.strip()
        lanche_id = lanche_dropdown.value
        bebida_id = bebidas_dropdow.value

        # A mesa é obrigatória, mas lanche e bebida não
        if not mesa_valor:
            snack_error("Informe o número da mesa antes de salvar.")
            return

        # Se nenhum lanche nem bebida for selecionado, não deixa salvar
        if not lanche_id and not bebida_id:
            snack_error("Selecione pelo menos um lanche ou uma bebida.")
            return

        carrinho = page.client_storage.get("carrinho_garcom") or []

        # Busca o lanche selecionado (se houver)
        lanche = None
        if lanche_id:
            lanche = next((l for l in lanches_disponiveis if l["id_lanche"] == int(lanche_id)), None)
            if not lanche:
                snack_error("Lanche selecionado não foi encontrado.")
                return

        # Busca a bebida selecionada (se houver)
        bebida = None
        if bebida_id:
            bebida = next((b for b in bebidas_disponiveis if b["id_bebida"] == int(bebida_id)), None)
            if not bebida:
                snack_error("Bebida selecionada não foi encontrada.")
                return

        # Cria um ou dois itens no carrinho, conforme a seleção
        if lanche:
            item_lanche = {
                "id_lanche": lanche["id_lanche"],
                "nome_lanche": lanche["nome_lanche"],
                "valor_lanche": lanche["valor_lanche"],
                "mesa": mesa_valor,
            }
            carrinho.append(item_lanche)

        if bebida:
            item_bebida = {
                "id_bebida": bebida["id_bebida"],
                "nome_bebida": bebida["nome_bebida"],
                "valor": bebida["valor"],
                "mesa": mesa_valor,
            }
            carrinho.append(item_bebida)

        # Atualiza o carrinho salvo
        page.client_storage.set("carrinho_garcom", carrinho)

        snack_sucesso(f"Pedido da Mesa {mesa_valor} adicionado com sucesso!")

        # Limpa campos
        numero_mesa.value = ""
        lanche_dropdown.value = ""
        bebidas_dropdow.value = ""

        # Atualiza dropdown de mesas abertas
        mesa_dropdown_aberta.options = [
            ft.dropdown.Option(m, f"Mesa {m}") for m in listar_mesas_abertas()
        ]
        page.update()

    # def salvar_carrinho(e):
    #     numero_mesaa = numero_mesa.value.strip()
    #     lanche_id = lanche_dropdown.value
    #     # pessoa_id_cliente = cliente_dropdown.value
    #
    #     if not numero_mesa or not lanche_id:
    #         snack_error("Preencha todos os campos antes de salvar.")
    #         return
    #
    #     carrinho = page.client_storage.get("carrinho_garcom") or []
    #     lanche = next((l for l in lanches_disponiveis if l["id_lanche"] == int(lanche_id)), None)
    #
    #     if not lanche:
    #         snack_error("Lanche não encontrado.")
    #         return
    #
    #     item_carrinho = {
    #         "id_lanche": lanche["id_lanche"],
    #         "nome_lanche": lanche["nome_lanche"],
    #         "valor_lanche": lanche["valor_lanche"],
    #         "mesa": numero_mesaa,  # importante: salvar a mesa
    #     }
    #
    #     snack_sucesso(f"Pedido da Mesa {numero_mesa} adicionado com sucesso!")
    #     numero_mesa.value = ""
    #     lanche_dropdown.value = ""
    #     # cliente_dropdown.value = ""
    #
    #     carrinho.append(item_carrinho)
    #     page.client_storage.set("carrinho_garcom", carrinho)
    #
    #     # Atualiza dropdown de mesas abertas
    #     mesa_dropdown_aberta.options = [ft.dropdown.Option(m, f"Mesa {m}") for m in listar_mesas_abertas()]
    #
    #     page.update()


    def listar_mesas_abertas():
        carrinho = page.client_storage.get("carrinho_garcom") or []
        mesas = set()
        for item in carrinho:
            mesas.add(str(item["mesa"]))
        return sorted(list(mesas))



    # 🔔 Modal de Confirmação (Pedido Presencial)
    def fechar_dialogo(e):
        dlg_modal.open = False
        page.update()
        print("✅ Pedido confirmado!")  # Aqui pode chamar cadastrar_vendas()

    dlg_modal = ft.AlertDialog(
        title=ft.Text("ALERTA‼️", color=Colors.BLACK),
        content=ft.Text(
            "Você realmente confirma esse pedido?\n"
            "Após cadastrado não terá como editar.\n"
            "Então chame o garçom mais próximo\n"
            "e se quiser alguma mudança já faça suas observações.",
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
            numero_mesa.value = ""
            lanche_dropdown.value = ""
            bebidas_dropdow.value = ""
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
                            ft.Divider(height=20),
                            ft.Text("Mesas Abertas", size=20, color=Colors.ORANGE_800),
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
                style=ft.ButtonStyle(bgcolor=Colors.PURPLE, color=Colors.BLACK, padding=15)
            )

            def tentar_fechar_mesa(e, mesa=mesa_num):
                token = page.client_storage.get("token")

                if not token:
                    snack_error("Garçom não logado!")
                    page.go("/login")
                    return

                try:
                    pedidos = listar_pedidos(token)
                except Exception as ex:
                    snack_error(f"Erro ao buscar pedidos: {ex}")
                    return

                # --- Filtra pedidos da mesa ---
                pedidos_mesa = []
                for p in pedidos:
                    if isinstance(p, str):
                        try:
                            p = json.loads(p)
                        except:
                            continue

                    numero_mesa = str(p.get("numero_mesa", "")).strip()
                    if numero_mesa == str(mesa):
                        pedidos_mesa.append(p)

                # --- Carrinho local da mesa ---
                carrinho_local = page.client_storage.get("carrinho_garcom") or []
                carrinho_da_mesa = [c for c in carrinho_local if str(c.get("mesa")) == str(mesa)]

                # --- Verifica se todos os pedidos da mesa estão enviados ---
                pedidos_pendentes = [p for p in pedidos_mesa if int(p.get("status", -1)) != 0]
                if pedidos_pendentes:
                    snack_error("Há pedidos dessa mesa ainda não enviados para a cozinha!")
                    page.update()
                    return

                # --- Verificação final ---
                if not carrinho_da_mesa:
                    snack_error(f"A mesa {mesa} não possui itens no carrinho local.")
                    page.update()
                    return

                # Tudo certo → vai para fechamento
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
                carrinho = page.client_storage.get("carrinho_garcom") or []

                for item in carrinho:
                    if item.get("id_lanche") == int(lanche_id):
                        return item
                return None


            print("não passou")

            def carregar_insumos_disponiveis(token):
                insumos = [i for i in listar_insumos(token) if i.get("qtd_insumo", 0) > 5]
                return (
                    {i["id_insumo"]: i["nome_insumo"] for i in insumos},  # nomes
                    {i["id_insumo"]: i["custo"] for i in insumos}  # preços
                )

            print("passou")

            # ==========================
            # Inicialização
            # ==========================
            lanche_id = get_lanche_por_id()
            print(lanche_id)
            item = carregar_carrinho_item(lanche_id)
            print("passei por aqui", item)
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
                carrinho = page.client_storage.get("carrinho_garcom") or []
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

                page.client_storage.set("carrinho_garcom", carrinho)

                page.snack_bar = ft.SnackBar(
                    ft.Text("Observações salvas com sucesso!"),
                    open=True, bgcolor=Colors.GREEN_700, duration=1500
                )
                page.update()
                page.go(f"/carrinho_garcom?mesa={item['mesa']}")

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
                            center_title=True, bgcolor=Colors.BLACK, actions=[btn_logout_observacoes]
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

            # --- Pega o carrinho do garçom e filtra pelo número da mesa ---
            carrinho = page.session.get("carrinho_garcom") or []
            carrinho_mesa = [item for item in carrinho if str(item.get("mesa")) == str(mesa_num)]

            # --- Verifica se há itens no carrinho ---
            if not carrinho_mesa:
                page.dialog = ft.AlertDialog(
                    title=ft.Text("Erro"),
                    content=ft.Text(f"Carrinho da mesa {mesa_num} está vazio."),
                    actions=[ft.ElevatedButton("Ok", on_click=lambda e: page.dialog.close())]
                )
                page.dialog.open = True
                page.update()
                return

            # --- Verifica se todos os pedidos foram enviados para a cozinha ---
            if not all(item.get("enviado_cozinha", False) for item in carrinho_mesa):
                page.dialog = ft.AlertDialog(
                    title=ft.Text("Atenção"),
                    content=ft.Text("Todos os pedidos devem ser enviados para a cozinha antes de fechar a mesa."),
                    actions=[ft.ElevatedButton("Ok", on_click=lambda e: page.dialog.close())]
                )
                page.dialog.open = True
                page.update()
                return

            # --- Lista de ingredientes disponíveis ---
            token = page.client_storage.get("token")
            insumos = listar_insumos(token)
            ingredientes_disponiveis = {i["id_insumo"]: i["nome_insumo"] for i in insumos}

            lista_itens = []
            total = 0

            for item in carrinho_mesa:
                total += item.get("valor_lanche", 0)
                item["valor_venda"] = item.get("valor_lanche", 0)

                obs_texto = item.get("observacoes_texto", "Nenhuma")
                receita_base = carregar_receita_base(item.get("id_lanche"))
                ingredientes_atual = item.get("ingredientes", {})

                adicionados, removidos = [], []
                for ing_id, qtd_atual in ingredientes_atual.items():
                    qtd_base = receita_base.get(ing_id, 0)
                    if qtd_atual > qtd_base:
                        adicionados.append(
                            f"{ingredientes_disponiveis.get(ing_id, str(ing_id))} (+{(qtd_atual - qtd_base) * 100}g)"
                        )
                    elif qtd_atual < qtd_base:
                        removidos.append(
                            f"{ingredientes_disponiveis.get(ing_id, str(ing_id))} (-{(qtd_base - qtd_atual) * 100}g)"
                        )

                lista_itens.append(
                    ft.Container(

                        content=ft.Column(

                            [
                                ft.Row(
                                    [

                                        ft.Text(item.get("nome_lanche", "Lanche"), color=Colors.ORANGE_700, size=16),
                                        ft.Text(f'R$ {item["valor_lanche"]:.2f}', color=Colors.YELLOW_900, size=14),

                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),

                                ft.Text(f"Obs: {obs_texto}", color=Colors.YELLOW_800, size=12),
                                ft.Text(
                                    "Adicionados: " + (", ".join(adicionados) if adicionados else "Nenhum"),
                                    color=Colors.GREEN_700, size=12
                                ),
                                ft.Text(
                                    "Removidos: " + (", ".join(removidos) if removidos else "Nenhum"),
                                    color=Colors.RED_700, size=12
                                ),


                            ]
                        ),
                        padding=15,
                        bgcolor=Colors.BLACK,
                        border_radius=10,


                    )
                )

            lista_itens_bebida = []

            for item in carrinho_mesa:
                total += item.get("valor", 0)
                item["valor_venda"] = item.get("valor", 0)

                lista_itens_bebida.append(
                    ft.Container(

                        content=ft.Column(
                            [
                                ft.Row(

                                    [

                                        ft.Text(item.get("nome_bebida", "bebida"), color=Colors.ORANGE_700, size=16),
                                        ft.Text(f'R$ {item["valor"]:.2f}', color=Colors.YELLOW_900, size=14),


                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),



                            ]
                        ),
                        padding=15,
                        bgcolor=Colors.BLACK,
                        border_radius=10,

                    )
                )


            total_label = ft.Text(
                f"Total da Mesa {mesa_num}: R$ {total:.2f}",
                font_family="Arial",
                color=Colors.ORANGE_700,
                size=20,
            )

            btn_fechar_venda = ft.ElevatedButton(
                "Confirmar Venda",
                bgcolor=Colors.ORANGE_700,
                on_click=lambda e: confirmar_venda_garcom(e)
            )

            btn_voltar = ft.ElevatedButton(
                "Voltar",
                bgcolor=Colors.ORANGE_100,
                on_click=lambda e: page.go("/mesa")
            )

            # --- Monta a view ---
            page.views.append(
                ft.View(
                    "/carrinho_garcom",
                    [
                        ft.AppBar(
                            title=ft.Text(f"Carrinho - Mesa {mesa_num}", color=Colors.ORANGE_700 ),
                            center_title=True,
                            bgcolor=Colors.BLACK,
                        ),
                        ft.Text(f"Resumo", color=Colors.BLACK, size=20, font_family="Arial"),

                        ft.Column(
                            [
                                ft.ListView(controls=lista_itens, expand=True),
                                ft.ListView(controls=lista_itens_bebida, expand=True),
                                total_label,
                                input_forma_pagamento,
                                ft.Row(
                                    [btn_fechar_venda, btn_voltar],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=20,
                                ),
                            ],
                            spacing=20,
                            expand=True,
                            scroll=True,
                        ),
                    ],
                    bgcolor=Colors.YELLOW_100,
                )
            )

            page.update()

        if page.route == "/presencial_delivery":
            page.views.append(
                View(
                    "/presencial_delivery",
                    [
                        AppBar(
                            title=ft.Image(src="imgdois.png", width=90),
                            center_title=True,
                            bgcolor=Colors.BLACK,
                            color=Colors.ORANGE_500,
                            title_spacing=5,
                            leading=logo,
                            actions=[btn_logout]
                        ),

                        ElevatedButton(
                            "Presencial",
                            on_click=lambda _: page.go("/cardapio_presencial"),
                            style=ButtonStyle(
                                shape={"": RoundedRectangleBorder(radius=15)},
                                padding=20,
                                bgcolor=Colors.ORANGE_600,
                                color=Colors.BLACK
                            )
                        ),
                        ElevatedButton(
                            "Delivery",
                            on_click=lambda _: page.go("/cardapio_delivery"),
                            style=ButtonStyle(
                                shape={"": RoundedRectangleBorder(radius=15)},
                                padding=20,
                                bgcolor=Colors.BLACK,
                                color=Colors.ORANGE_400
                            )
                        ),

                    ],
                    bgcolor=Colors.ORANGE_800,
                    spacing=20  # só define o espaçamento entre eles
                )
            )

        if page.route == "/cardapio_presencial":
            cardapio_bebidas(e)
            cardapio(e)
            page.views.append(
                View(
                    "/cardapio",
                    [
                        AppBar(title=ft.Image(src="imgdois.png", width=90), center_title=True, bgcolor=Colors.BLACK,
                               color=Colors.PURPLE, title_spacing=5, leading=logo, actions=[btn_logout]),

                                t



                    ],
                    bgcolor=Colors.BLACK,
                )
            )

        if page.route == "/cardapio_delivery":
            cardapio_delivery(e)
            cardapio_delivery_bebida(e)

            page.views.append(
                View(
                    "/cardapio",
                    [
                        AppBar(title=ft.Image(src="imgdois.png", width=90), center_title=True, bgcolor=Colors.BLACK,
                               color=Colors.PURPLE, title_spacing=5, leading=logo, actions=[btn_logout]),

                        t

                    ],
                    bgcolor=Colors.BLACK,
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

            valor_base_original = item.get("valor_original_lanche", item.get("valor_lanche", 0))
            item["valor_original_lanche"] = valor_base_original

            lanche_id = item.get("id_lanche")
            receita_original = carregar_receita_base(lanche_id) if lanche_id else {}

            # Mantém alterações salvas ou receita original
            ingredientes_salvos = item.get("ingredientes") or {}
            item["ingredientes"] = {ing_id: ingredientes_salvos.get(ing_id, receita_original.get(ing_id, 0))
                                    for ing_id in ingredientes_disponiveis}

            # ==========================
            # UI e funções de controle
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

                    item_copy.update({
                        "observacoes_texto": obs_input.value or "Nenhuma",
                        "ingredientes": valores_atualizados,
                        "valor_lanche": atualizar_preco(),
                        "valor_venda": atualizar_preco(),
                        "observacoes": observacoes
                    })
                    carrinho[lanche_index] = item_copy
                    page.client_storage.set("carrinho", carrinho)

                    page.snack_bar = ft.SnackBar(
                        ft.Text("Observações salvas com sucesso!"),
                        open=True, bgcolor=Colors.GREEN_700, duration=1500
                    )
                    page.update()
                page.go("/carrinho")

            atualizar_preco()

            # ==========================
            # Montagem da view
            # ==========================
            page.views.append(
                ft.View(
                    "/observacoes",
                    [
                        ft.AppBar(title=ft.Text("Personalizar Lanche", size=22, color=Colors.ORANGE_900, weight="bold"),
                                  center_title=True, bgcolor=Colors.BLACK, actions=[btn_logout_observacoes_garcom]),
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

        if page.route == "/vendas":
            input_forma_pagamento.value = ""
            input_endereco.value = ""

            carrinho = page.client_storage.get("carrinho") or []

            # Ingredientes disponíveis
            token = page.client_storage.get("token")
            insumos = listar_insumos(token)
            ingredientes_disponiveis = {i["id_insumo"]: i["nome_insumo"] for i in insumos}

            lista_itens = []
            total = 0.0
            # lanches = [i for i in carrinho if []]
            lanches = [i for i in carrinho if "valor_lanche" in i]


            for item in lanches:
                total += item.get("valor_lanche", 0)
                item["valor_venda"] = item.get("valor_lanche", 0)
                # ... resto do código de lanche

                obs_texto = item.get("observacoes_texto", "Nenhuma")
                receita_base = carregar_receita_base(item.get("id_lanche"))
                ingredientes_atual = item.get("ingredientes", {})

                adicionados = []
                removidos = []

                for ing_id, qtd_atual in ingredientes_atual.items():
                    qtd_base = receita_base.get(ing_id, 0)
                    if qtd_atual > qtd_base:
                        adicionados.append(
                            f"{ingredientes_disponiveis.get(ing_id, str(ing_id))} (+{(qtd_atual - qtd_base) * 100}g)"
                        )
                    elif qtd_atual < qtd_base:
                        removidos.append(
                            f"{ingredientes_disponiveis.get(ing_id, str(ing_id))} (-{(qtd_base - qtd_atual) * 100}g)"
                        )

                lista_itens.append(
                    ft.Container(

                        content=ft.Column(

                            [
                                ft.Row(
                                    [

                                        ft.Text(item.get("nome_lanche", "Lanche"), color=Colors.ORANGE_700, size=16),
                                        ft.Text(f'R$ {item["valor_lanche"]:.2f}', color=Colors.YELLOW_900, size=14),

                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),

                                ft.Text(f"Obs: {obs_texto}", color=Colors.YELLOW_800, size=12),
                                ft.Text(
                                    "Adicionados: " + (", ".join(adicionados) if adicionados else "Nenhum"),
                                    color=Colors.GREEN_700, size=12
                                ),
                                ft.Text(
                                    "Removidos: " + (", ".join(removidos) if removidos else "Nenhum"),
                                    color=Colors.RED_700, size=12
                                ),

                            ]
                        ),
                        padding=15,
                        bgcolor=Colors.BLACK,
                        border_radius=10,

                    )
                )

            lista_itens_bebida = []

            bebidas = [i for i in carrinho if "valor" in i]

            for item in bebidas:
                total += item.get("valor", 0)
                item["valor_venda"] = item.get("valor", 0)
                # ... resto do código de bebida

                lista_itens_bebida.append(
                    ft.Container(

                        content=ft.Column(
                            [
                                ft.Row(

                                    [

                                        ft.Text(item.get("nome_bebida", "bebida"), color=Colors.ORANGE_700, size=16),
                                        ft.Text(f'R$ {item["valor"]:.2f}', color=Colors.YELLOW_900, size=14),

                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),

                            ]
                        ),
                        padding=15,
                        bgcolor=Colors.BLACK,
                        border_radius=10,

                    )
                )

            page.client_storage.set("carrinho", carrinho)
            total_label = ft.Text(f"Total do Pedido: R$ {total:.2f}", color=Colors.ORANGE_700, size=20)

            # Monta a view final
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
                                    input_endereco,
                                    input_forma_pagamento,
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                text="Confirmar Venda",
                                                bgcolor=Colors.ORANGE_800,
                                                color=Colors.BLACK,
                                                on_click=confirmar_venda(e),
                                            ),
                                            print("asdfghjkj"),
                                            ft.OutlinedButton(
                                                "Voltar",
                                                on_click=lambda e: page.go("/carrinho"),
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=20,
                                    )]
                                ),

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
        width=80, opacity=0.7,

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
        on_click=lambda _: page.go('/cardapio_delivery'),
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
    t = ft.Tabs(

        selected_index=1,
        animation_duration=300,

        tabs=[

            ft.Tab(
                text="Bebidas",
                icon=ft.Icons.LOCAL_DRINK,
                content=ft.Container(
                    lv_bebidas,
                ),
            ),

            ft.Tab(
                text="Lanches",
                icon=ft.Icons.FOOD_BANK,
                content=ft.Container(
                    lv_lanches,

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

    lanche_dropdown = ft.Dropdown(
        label="Selecione o Lanche",
        width=250,
        border_color=Colors.PURPLE,
        color=Colors.BLACK,
        bgcolor=Colors.DEEP_ORANGE_100,
        options=[ft.dropdown.Option(str(l["id_lanche"]), l["nome_lanche"]) for l in lanches_disponiveis]
    )

    bebidas_dropdow = ft.Dropdown(
        label="Selecione a bebida",
        width=250,
        border_color=Colors.PURPLE,
        color=Colors.BLACK,
        bgcolor=Colors.DEEP_ORANGE_100,
        options=[ft.dropdown.Option(str(b["id_bebida"]), b["nome_bebida"]) for b in bebidas_disponiveis  ]
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