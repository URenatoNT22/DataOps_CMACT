/* =====================================================================================
   SETUP 02 - Datos FICTICIOS para la demo
   Se ejecuta sobre una base ya desplegada (BI_DEV, BI_PROD o la base efímera de CI).
   Normalmente lo lanza el workflow "Datos de demo" (Actions), pero también se puede
   ejecutar a mano en SSMS conectado a la base correspondiente.

   - Genera clientes, agencias, productos, créditos y cuotas en el esquema src.
   - Es DETERMINÍSTICO: el mismo script genera los mismos datos en DEV y en PROD,
     así los indicadores son comparables entre ambientes.
   - Luego carga los tablones para los últimos @MESES fines de mes.

   TODOS LOS DATOS SON INVENTADOS. Nombres, documentos y agencias no corresponden a
   personas ni a oficinas reales.
   ===================================================================================== */
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @N_CLIENTES INT  = 2000;
DECLARE @N_CREDITOS INT  = 3000;
DECLARE @MESES      INT  = 6;
DECLARE @HOY        DATE = CAST(SYSDATETIME() AS DATE);

PRINT N'Limpiando datos previos...';
DELETE FROM [tab].[TB_CRONOGRAMA];
DELETE FROM [tab].[TB_CREDITO];
DELETE FROM [src].[CUOTA];
DELETE FROM [src].[CREDITO];
DELETE FROM [src].[CLIENTE];
DELETE FROM [src].[AGENCIA];
DELETE FROM [src].[PRODUCTO];

/* ---------- Catálogos ---------- */
INSERT INTO [src].[AGENCIA] ([ID_AGENCIA], [NOMBRE_AGENCIA], [REGION], [ZONA]) VALUES
 (1,  'AG. CENTRO',          'LA LIBERTAD', 'NORTE'),
 (2,  'AG. LA ESPERANZA',    'LA LIBERTAD', 'NORTE'),
 (3,  'AG. EL PORVENIR',     'LA LIBERTAD', 'NORTE'),
 (4,  'AG. CHEPEN',          'LA LIBERTAD', 'NORTE'),
 (5,  'AG. CHICLAYO NORTE',  'LAMBAYEQUE',  'NORTE'),
 (6,  'AG. PIURA CASTILLA',  'PIURA',       'NORTE'),
 (7,  'AG. CAJAMARCA PLAZA', 'CAJAMARCA',   'SIERRA'),
 (8,  'AG. HUARAZ',          'ANCASH',      'SIERRA'),
 (9,  'AG. CHIMBOTE',        'ANCASH',      'COSTA'),
 (10, 'AG. TUMBES',          'TUMBES',      'NORTE'),
 (11, 'AG. LIMA NORTE',      'LIMA',        'LIMA'),
 (12, 'AG. LIMA SUR',        'LIMA',        'LIMA');

INSERT INTO [src].[PRODUCTO] ([ID_PRODUCTO], [NOMBRE_PRODUCTO], [TIPO_CREDITO], [MONEDA]) VALUES
 (1, 'CONSUMO LIBRE DISPONIBILIDAD', 'CONSUMO',         'PEN'),
 (2, 'MICRO CAPITAL DE TRABAJO',     'MICROEMPRESA',    'PEN'),
 (3, 'MICRO ACTIVO FIJO',            'MICROEMPRESA',    'PEN'),
 (4, 'PEQUENA EMPRESA',              'PEQUENA EMPRESA', 'PEN'),
 (5, 'HIPOTECARIO VIVIENDA',         'HIPOTECARIO',     'PEN'),
 (6, 'CONSUMO DOLARES',              'CONSUMO',         'USD');

/* ---------- Diccionarios de nombres inventados ---------- */
DECLARE @NOMBRES TABLE ([I] INT PRIMARY KEY, [V] VARCHAR(30));
INSERT INTO @NOMBRES VALUES (0,'ANA'),(1,'LUIS'),(2,'ROSA'),(3,'JORGE'),(4,'CARMEN'),(5,'PEDRO'),(6,'JULIA'),
 (7,'MIGUEL'),(8,'ELENA'),(9,'CARLOS'),(10,'SOFIA'),(11,'RAUL'),(12,'LUCIA'),(13,'MARIO'),(14,'TERESA'),
 (15,'VICTOR'),(16,'PAOLA'),(17,'HUGO'),(18,'NORMA'),(19,'CESAR');
DECLARE @APELLIDOS TABLE ([I] INT PRIMARY KEY, [V] VARCHAR(30));
INSERT INTO @APELLIDOS VALUES (0,'QUISPE'),(1,'RAMOS'),(2,'TORRES'),(3,'VARGAS'),(4,'CASTILLO'),(5,'MENDOZA'),
 (6,'ROJAS'),(7,'SALAZAR'),(8,'HUAMAN'),(9,'CHAVEZ'),(10,'FLORES'),(11,'REYES'),(12,'PAREDES'),(13,'DIAZ'),
 (14,'VEGA'),(15,'CRUZ'),(16,'LEON'),(17,'SILVA'),(18,'NAVARRO'),(19,'CAMPOS');

/* ---------- Números auxiliares ---------- */
DECLARE @MAXN INT = CASE WHEN @N_CREDITOS > @N_CLIENTES THEN @N_CREDITOS ELSE @N_CLIENTES END;
IF OBJECT_ID('tempdb..#N') IS NOT NULL DROP TABLE #N;
SELECT TOP (@MAXN) CAST(ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS INT) AS [n]
INTO #N
FROM sys.all_objects AS [a] CROSS JOIN sys.all_objects AS [b];
CREATE UNIQUE CLUSTERED INDEX [IX_N] ON #N ([n]);

/* ---------- Clientes ---------- */
PRINT N'Generando clientes...';
INSERT INTO [src].[CLIENTE] ([ID_CLIENTE], [TIPO_DOCUMENTO], [NRO_DOCUMENTO], [NOMBRE_COMPLETO], [FECHA_NACIMIENTO], [SEXO], [SEGMENTO], [FECHA_ALTA])
SELECT
    [x].[n],
    CASE WHEN [x].[n] % 15 = 0 THEN 'RUC' ELSE 'DNI' END,
    CASE WHEN [x].[n] % 15 = 0 THEN '20' + RIGHT('000000000' + CAST([x].[n] AS VARCHAR(9)), 9)
         ELSE '9' + RIGHT('0000000' + CAST([x].[n] AS VARCHAR(7)), 7) END,
    CASE WHEN [x].[n] % 15 = 0 THEN 'EMPRESA FICTICIA ' + CAST([x].[n] AS VARCHAR(10)) + ' S.A.C.'
         ELSE [a1].[V] + ' ' + [a2].[V] + ', ' + [nm].[V] END,
    CASE WHEN [x].[n] % 15 = 0 THEN NULL ELSE DATEADD(DAY, -(18 * 365 + [h].[h1] % (45 * 365)), @HOY) END,
    CASE WHEN [x].[n] % 15 = 0 THEN NULL WHEN [h].[h2] % 2 = 0 THEN 'F' ELSE 'M' END,
    CASE WHEN [x].[n] % 15 = 0 THEN 'PEQUENA'
         WHEN [h].[h3] % 10 < 5 THEN 'MICRO'
         WHEN [h].[h3] % 10 < 9 THEN 'CONSUMO'
         ELSE 'PREFERENTE' END,
    DATEADD(DAY, -(400 + [h].[h4] % 3000), @HOY)
FROM #N AS [x]
CROSS APPLY (SELECT HASHBYTES('SHA2_256', CONCAT('cli', [x].[n])) AS [hb]) AS [z]
CROSS APPLY (SELECT CAST(SUBSTRING([z].[hb], 1, 4) AS INT) & 2147483647 AS [h1],
                    CAST(SUBSTRING([z].[hb], 5, 4) AS INT) & 2147483647 AS [h2],
                    CAST(SUBSTRING([z].[hb], 9, 4) AS INT) & 2147483647 AS [h3],
                    CAST(SUBSTRING([z].[hb], 13, 4) AS INT) & 2147483647 AS [h4],
                    CAST(SUBSTRING([z].[hb], 17, 4) AS INT) & 2147483647 AS [h5]) AS [h]
INNER JOIN @NOMBRES   AS [nm] ON [nm].[I] = [h].[h5] % 20
INNER JOIN @APELLIDOS AS [a1] ON [a1].[I] = [h].[h1] % 20
INNER JOIN @APELLIDOS AS [a2] ON [a2].[I] = [h].[h3] % 20
WHERE [x].[n] <= @N_CLIENTES;

/* ---------- Créditos ---------- */
PRINT N'Generando créditos...';
INSERT INTO [src].[CREDITO] ([ID_CREDITO], [COD_CREDITO], [ID_CLIENTE], [ID_AGENCIA], [ID_PRODUCTO], [ANALISTA],
                             [FECHA_DESEMBOLSO], [MONTO_DESEMBOLSADO], [TASA_ANUAL], [NRO_CUOTAS])
SELECT
    [x].[n],
    'CR' + RIGHT('00000000' + CAST([x].[n] AS VARCHAR(8)), 8),
    1 + [h].[h1] % @N_CLIENTES,
    CAST(1 + [h].[h2] % 12 AS SMALLINT),
    [p].[ID_PRODUCTO],
    'ANALISTA ' + RIGHT('00' + CAST(1 + [h].[h4] % 25 AS VARCHAR(2)), 2),
    DATEADD(DAY, -(15 + [h].[h5] % 1080), @HOY),
    CAST(ROUND(CASE [p].[ID_PRODUCTO]
                  WHEN 1 THEN 1000   + [h].[h6] % 19000
                  WHEN 2 THEN 2000   + [h].[h6] % 28000
                  WHEN 3 THEN 5000   + [h].[h6] % 45000
                  WHEN 4 THEN 20000  + [h].[h6] % 130000
                  WHEN 5 THEN 80000  + [h].[h6] % 220000
                  ELSE        1000   + [h].[h6] % 9000 END, -2) AS DECIMAL(18,2)),
    CAST(CASE [p].[ID_PRODUCTO]
            WHEN 1 THEN 35 + ([h].[h7] % 2000) / 100.0
            WHEN 2 THEN 30 + ([h].[h7] % 1500) / 100.0
            WHEN 3 THEN 28 + ([h].[h7] % 1200) / 100.0
            WHEN 4 THEN 18 + ([h].[h7] % 1000) / 100.0
            WHEN 5 THEN  9 + ([h].[h7] %  300) / 100.0
            ELSE        15 + ([h].[h7] % 1000) / 100.0 END AS DECIMAL(9,4)),
    CAST(CASE WHEN [p].[ID_PRODUCTO] = 5 THEN 60
              ELSE CHOOSE(1 + [h].[h8] % 5, 6, 12, 18, 24, 36) END AS SMALLINT)
FROM #N AS [x]
CROSS APPLY (SELECT HASHBYTES('SHA2_256', CONCAT('cre', [x].[n])) AS [hb]) AS [z]
CROSS APPLY (SELECT CAST(SUBSTRING([z].[hb], 1, 4) AS INT) & 2147483647 AS [h1],
                    CAST(SUBSTRING([z].[hb], 5, 4) AS INT) & 2147483647 AS [h2],
                    CAST(SUBSTRING([z].[hb], 9, 4) AS INT) & 2147483647 AS [h3],
                    CAST(SUBSTRING([z].[hb], 13, 4) AS INT) & 2147483647 AS [h4],
                    CAST(SUBSTRING([z].[hb], 17, 4) AS INT) & 2147483647 AS [h5],
                    CAST(SUBSTRING([z].[hb], 21, 4) AS INT) & 2147483647 AS [h6],
                    CAST(SUBSTRING([z].[hb], 25, 4) AS INT) & 2147483647 AS [h7],
                    CAST(SUBSTRING([z].[hb], 29, 4) AS INT) & 2147483647 AS [h8]) AS [h]
CROSS APPLY (SELECT CAST(CASE WHEN [h].[h3] % 100 < 30 THEN 1
                              WHEN [h].[h3] % 100 < 55 THEN 2
                              WHEN [h].[h3] % 100 < 70 THEN 3
                              WHEN [h].[h3] % 100 < 82 THEN 4
                              WHEN [h].[h3] % 100 < 90 THEN 5
                              ELSE 6 END AS SMALLINT) AS [ID_PRODUCTO]) AS [p]
WHERE [x].[n] <= @N_CREDITOS;

/* ---------- Cuotas (sistema francés) y comportamiento de pago ---------- */
PRINT N'Generando cronogramas y pagos...';
WITH [K] AS
(
    SELECT [c].[ID_CREDITO], [c].[FECHA_DESEMBOLSO], [c].[NRO_CUOTAS],
           CAST([c].[MONTO_DESEMBOLSADO] AS FLOAT) AS [P],
           CAST([c].[TASA_ANUAL] AS FLOAT) / 100.0 / 12.0 AS [r],
           [k].[n] AS [NRO_CUOTA],
           [perfil].[PERFIL], [perfil].[CUOTA_QUIEBRE]
    FROM [src].[CREDITO] AS [c]
    INNER JOIN #N AS [k] ON [k].[n] <= [c].[NRO_CUOTAS]
    CROSS APPLY (SELECT HASHBYTES('SHA2_256', CONCAT('pag', [c].[ID_CREDITO])) AS [hb]) AS [z]
    CROSS APPLY (SELECT (CAST(SUBSTRING([z].[hb], 1, 4) AS INT) & 2147483647) % 100 AS [PERFIL],
                        1 + (CAST(SUBSTRING([z].[hb], 5, 4) AS INT) & 2147483647) % [c].[NRO_CUOTAS] AS [CUOTA_QUIEBRE]) AS [perfil]
),
[S] AS
(
    SELECT [K].*,
           [K].[P] * [K].[r] / (1 - POWER(1 + [K].[r], -CAST([K].[NRO_CUOTAS] AS FLOAT))) AS [C]
    FROM [K]
),
[B] AS
(
    SELECT [S].*,
           ROUND([S].[P] * POWER(1 + [S].[r], [S].[NRO_CUOTA] - 1)
                 - [S].[C] * (POWER(1 + [S].[r], [S].[NRO_CUOTA] - 1) - 1) / [S].[r], 2) AS [SALDO_ANT],
           CASE WHEN [S].[NRO_CUOTA] = [S].[NRO_CUOTAS] THEN 0
                ELSE ROUND([S].[P] * POWER(1 + [S].[r], [S].[NRO_CUOTA])
                           - [S].[C] * (POWER(1 + [S].[r], [S].[NRO_CUOTA]) - 1) / [S].[r], 2) END AS [SALDO_POST]
    FROM [S]
),
[Q] AS
(
    SELECT [B].[ID_CREDITO], [B].[NRO_CUOTA],
           DATEADD(MONTH, [B].[NRO_CUOTA], [B].[FECHA_DESEMBOLSO]) AS [FECHA_VENCIMIENTO],
           CAST([B].[SALDO_ANT] - [B].[SALDO_POST] AS DECIMAL(18,2)) AS [CAPITAL],
           CAST(ROUND([B].[SALDO_ANT] * [B].[r], 2) AS DECIMAL(18,2)) AS [INTERES],
           [B].[PERFIL], [B].[CUOTA_QUIEBRE],
           (CAST(SUBSTRING(HASHBYTES('SHA2_256', CONCAT('cuo', [B].[ID_CREDITO], '-', [B].[NRO_CUOTA])), 1, 4) AS INT) & 2147483647) AS [hq]
    FROM [B]
)
INSERT INTO [src].[CUOTA] ([ID_CREDITO], [NRO_CUOTA], [FECHA_VENCIMIENTO], [CAPITAL], [INTERES], [FECHA_PAGO], [MONTO_PAGADO])
SELECT [Q].[ID_CREDITO], [Q].[NRO_CUOTA], [Q].[FECHA_VENCIMIENTO], [Q].[CAPITAL], [Q].[INTERES],
       CASE WHEN [pg].[FECHA_PAGO] <= @HOY THEN [pg].[FECHA_PAGO] END,
       CASE WHEN [pg].[FECHA_PAGO] <= @HOY THEN [Q].[CAPITAL] + [Q].[INTERES] END
FROM [Q]
CROSS APPLY
(
    SELECT CASE
             WHEN [Q].[PERFIL] < 72 THEN DATEADD(DAY, ([Q].[hq] % 8) - 3, [Q].[FECHA_VENCIMIENTO])          -- puntual
             WHEN [Q].[PERFIL] < 88 THEN DATEADD(DAY, 5 + [Q].[hq] % 40, [Q].[FECHA_VENCIMIENTO])           -- paga con atraso
             WHEN [Q].[NRO_CUOTA] < [Q].[CUOTA_QUIEBRE] THEN DATEADD(DAY, [Q].[hq] % 10, [Q].[FECHA_VENCIMIENTO])
             ELSE NULL                                                                                       -- deja de pagar
           END AS [FECHA_PAGO]
) AS [pg];

DECLARE @C1 INT = (SELECT COUNT(*) FROM [src].[CLIENTE]),
        @C2 INT = (SELECT COUNT(*) FROM [src].[CREDITO]),
        @C3 INT = (SELECT COUNT(*) FROM [src].[CUOTA]);
PRINT CONCAT(N'Clientes: ', @C1, N' | Créditos: ', @C2, N' | Cuotas: ', @C3);

/* ---------- Carga de tablones para los últimos @MESES fines de mes ---------- */
DECLARE @i INT = @MESES, @F DATE;
WHILE @i >= 1
BEGIN
    SET @F = EOMONTH(@HOY, -@i);
    PRINT CONCAT(N'Cargando tablones al ', CONVERT(VARCHAR(10), @F, 23), N'...');
    EXEC [ctl].[usp_CARGA_DIARIA] @FECHA_CORTE = @F;
    SET @i -= 1;
END

PRINT N'Datos ficticios generados.';
