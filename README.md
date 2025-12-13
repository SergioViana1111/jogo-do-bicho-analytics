# Jogo do Bicho Analytics

Painel interativo de análise estatística do Jogo do Bicho desenvolvido com Streamlit.

## Funcionalidades

- 📊 Dashboard com rankings e gráficos interativos
- 🔁 Análise de repetições (grupos, centenas, milhares)
- 📈 Ranking de linhas por grupo
- 🎯 Fechamentos inteligentes
- 📤 Upload de planilha CSV/Excel

## Como Executar Localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Formato da Planilha

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| data | Data do sorteio | 2025-12-01 |
| loteria | Nome da loteria | RJ, Nacional, Look GO, Federal, Capital |
| horario | Horário | 11:00 |
| grupo | Grupo (1-25) | 7 |
| centena | Centena (0-999) | 345 |
| milhar | Milhar (0-9999) | 7345 |

## ⚠️ Aviso

Este sistema é para análise estatística apenas. Resultados passados não garantem resultados futuros.
