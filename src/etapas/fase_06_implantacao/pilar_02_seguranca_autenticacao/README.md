# 🔐 `src/etapas/fase_06_implantacao/pilar_02_seguranca_autenticacao/` — Segurança e autenticação

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_06](../README.md)

## 🎯 Objetivo

Emitir e validar credenciais JWT para proteger as rotas da API, garantindo
identidade, perfil de acesso e vigência temporal conforme RFC 7519 e RFC 6750.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Credenciais (`usuario`, `senha`) e cabeçalho `Authorization: Bearer <token>`. |
| **Processa** | Assinatura HMAC-SHA256, expiração, decodificação e verificação de claims. |
| **Entrega para** | Pilar 4: requisição autorizada ou `HTTP 401 Unauthorized`. |
| **Quem consome** | Rotas FastAPI protegidas e clientes HTTP. |

## 🧩 Arquivos

| Arquivo | Classe / função | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `gerenciador_token_jwt.py` | `GerenciadorTokenJWT` | `sub`, `papel`, segredo e validade. | Cria/valida JWT com HS256. | Token `str` ou `dict` decodificado / `None`. |
| `guardiao_autorizacao.py` | `verificar_autorizacao_portador` | `HTTPAuthorizationCredentials` do FastAPI. | Extrai o Bearer, valida e devolve o usuário. | `dict` do usuário ou `HTTPException 401`. |

## 📥 Entradas

| Entrada | Formato | Origem |
| :--- | :--- | :--- |
| Usuário | `str` | Corpo do login |
| Senha | `str` | Corpo do login |
| Segredo | `str` ≥ 32 bytes | Variável de ambiente |
| Algoritmo | `str` | Padrão `HS256` |
| Validade | `int` minutos | Padrão `480` (8h) |
| Token | `str` no header | Cliente |

## 📤 Saídas

| Saída | Formato | Consumidor |
| :--- | :--- | :--- |
| `access_token` | JWT assinado | Cliente |
| `token_type` | `"bearer"` | Cliente |
| `expira_em_minutos` | `int` | Cliente |
| Claims decodificadas | `dict` (`sub`, `papel`, `exp`, `iat`) | Rotas protegidas |
| Erro de autenticação | `HTTP 401` | Cliente |

## 🔁 Fluxo

```text
POST /autenticacao/token
        │ usuario + senha
        ▼
GerenciadorTokenJWT.gerar_token_acesso()
        │ payload: sub, papel, iat, exp
        ▼
JWT assinado (HS256)
        │
        ▼
Cliente envia: Authorization: Bearer <token>
        │
        ▼
verificar_autorizacao_portador()
        ├── token válido   → rota protegida
        └── inválido/expirado/ausente → HTTP 401
```

## 📌 Regras

- Em produção, a chave **nunca** deve usar o valor padrão do código; injete via
  variável de ambiente.
- O algoritmo deve ser fixado (`HS256`); nunca aceite `alg` arbitrário do token.
- Tokens expirados, adulterados ou ausentes resultam em `401`.
- O guardião não decide regras de negócio; apenas autentica.
- O tempo padrão de 480 minutos pode ser reduzido por política de segurança.

## 🔗 Ligações

- Rota de login e uso do guardião: [pilar_04](../pilar_04_motor_inferencia_api/README.md).
- Teste de segurança: [`scripts/executores_arquivo/fase_06_pilar_02_seguranca.py`](../../../../scripts/executores_arquivo/fase_06_pilar_02_seguranca.py).
- Voltar para [fase_06](../README.md).
