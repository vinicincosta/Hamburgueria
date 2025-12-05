Autenticação e Autorização
Login de Usuário - O sistema deve permitir que um usuário faça login fornecendo e-mail e senha.

Verificação de Credenciais - O sistema deve verificar as credenciais de login através da função routes_web.post_login.

Geração de Token de Sessão - O sistema deve gerar e armazenar um access_token na sessão do Flask após um login bem-sucedido.

Redirecionamento Pós-Login (Admin) - O sistema deve redirecionar um usuário com o papel 'admin' para a rota /faturamento (faturamento).

Redirecionamento Pós-Login (Cozinha) - O sistema deve redirecionar um usuário com o papel 'cozinha' para a rota /pedidos (pedidos).

Controle de Acesso por Token - O sistema deve verificar a existência de um token de sessão (verificar_token) antes de permitir o acesso a páginas restritas e, se ausente, redirecionar para a página de login.

Controle de Acesso por Papel - O sistema deve restringir o acesso a rotas específicas (ex: /pessoas, /entradas, /insumos, /categorias) com base no papel do usuário na sessão.

Logout de Usuário - O sistema deve permitir que um usuário faça logout, limpando a sessão e redirecionando para a página de login.

👨‍👩‍• Gerenciamento de Pessoas
Visualizar Pessoas - O sistema deve permitir que um usuário admin visualize a lista de todos os usuários (/pessoas), buscando os dados via routes_web.get_pessoas.

Cadastrar Funcionário - O sistema deve permitir que um usuário admin cadastre uma nova pessoa/funcionário (com CPF, Nome, Email, Senha, Salário e Papel), utilizando routes_web.post_cadastro_pessoas.

Editar Pessoa - O sistema deve permitir que um usuário admin edite qualquer pessoa, ou que o próprio usuário edite sua conta. O sistema deve utilizar routes_web.put_editar_pessoa para atualizar os dados (nome, cpf, salário, papel, senha, email, status).

• Gerenciamento de Lanches e Receitas
Visualizar Lanches - O sistema deve permitir a visualização da lista de lanches (/lanches), buscando dados via routes_web.get_lanches.

Cadastrar Lanche - O sistema deve permitir que um usuário admin cadastre um novo lanche (com nome, descrição e valor), utilizando routes_web.post_lanches.

Visualizar Relação Lanche-Insumo - O sistema deve permitir a visualização da lista de insumos por lanche (/lanche_insumos), buscando dados via routes_web.get_lanche_insumos.

Cadastrar Receita (Lanche-Insumo) - O sistema deve permitir que um usuário admin cadastre uma relação insumo-lanche (receita), especificando a quantidade, utilizando routes_web.post_lanche_insumos.

• Gerenciamento de Insumos e Categorias
Visualizar Insumos - O sistema deve permitir a visualização da lista de insumos (/insumos), buscando dados via routes_web.get_insumos.

Visualizar Insumo por ID - O sistema deve permitir a visualização de um insumo específico pelo seu ID.

Cadastrar Insumo - O sistema deve permitir que um usuário admin cadastre um novo insumo (com nome, custo e ID da categoria), utilizando routes_web.post_insumos.

Editar Insumo - O sistema deve permitir que um usuário admin edite um insumo (nome e ID da categoria), utilizando routes_web.put_editar_insumo.

Visualizar Categorias - O sistema deve permitir a visualização da lista de categorias (/categorias), buscando dados via routes_web.get_categorias.

Cadastrar Categoria - O sistema deve permitir que um usuário admin cadastre uma nova categoria (com nome), utilizando routes_web.post_categorias.

Editar Categoria - O sistema deve permitir que um usuário admin edite uma categoria (nome), utilizando routes_web.put_editar_categoria.

• Gerenciamento de Bebidas
Visualizar Bebidas - O sistema deve permitir a visualização da lista de bebidas (/bebidas), buscando dados via routes_web.get_bebidas.

Cadastrar Bebida - O sistema deve permitir que um usuário admin cadastre uma nova bebida (com nome, valor e ID da categoria), utilizando routes_web.post_bebidas.

•Gerenciamento de Entradas (Estoque)
Visualizar Entradas - O sistema deve permitir que um usuário admin visualize o histórico de entradas de estoque (/entradas), buscando dados via routes_web.get_entradas.

Cadastrar Entrada de Insumo - O sistema deve permitir que um usuário admin registre uma entrada de estoque para um insumo (com quantidade, ID do insumo, data, nota fiscal e valor), utilizando routes_web.post_entradas_insumos.

Cadastrar Entrada de Bebida - O sistema deve permitir que um usuário admin registre uma entrada de estoque para uma bebida (com quantidade, ID da bebida, data, nota fiscal e valor), utilizando routes_web.post_entradas_bebidas.

• Gerenciamento de Pedidos e Vendas
Visualizar Pedidos - O sistema deve permitir que usuários autorizados (ex: 'cozinha', 'admin', 'garcom') visualizem a lista de pedidos (/pedidos), buscando dados via routes_web.get_pedidos.

Visualizar Vendas - O sistema deve permitir que usuários autorizados (ex: 'admin', 'cozinha', 'garcom') visualizem a lista de vendas (/vendas), implementando um sistema de paginação (12 por página), buscando dados via routes_web.get_vendas.