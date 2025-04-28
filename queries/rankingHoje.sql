WITH Ranking AS (
    SELECT
        COUNT(MOV.CODIGO) AS quantidadeCheckInOut,
        SUM(MOV.VALORTOTAL) AS valorTotalCheckInOut,
        SUM(MOV.VALORLIQUIDO) AS valorLiquidoCheckInOut,
        MOV.CODIGO_PROJETO AS codigoEstoquista
    FROM MOVIMENTACOES MOV
    WHERE CODTIPOMOV IN ('2.1.06', '2.1.03')
        AND datageracao >= CONVERT(DATETIME, CAST(GETDATE() AS DATE))
    GROUP BY MOV.CODIGO_PROJETO
)
SELECT
    codigoProjeto,
    quantidadeCheckInOut,
    valorTotalCheckInOut,
    valorLiquidoCheckInOut,
    RANK() OVER (ORDER BY quantidadeCheckInOut DESC) AS rankQuantidade,
    RANK() OVER (ORDER BY valorTotalCheckInOut DESC) AS rankValorTotal,
    RANK() OVER (ORDER BY valorLiquidoCheckInOut DESC) AS rankValorLiquido
FROM Ranking;