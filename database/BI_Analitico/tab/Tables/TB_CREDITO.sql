-- Tablón de créditos: una fila por crédito con saldo a la fecha de corte, con todos los atributos de cliente, agencia y producto desnormalizados.
CREATE TABLE [tab].[TB_CREDITO]
(
    [FECHA_CORTE] DATE NOT NULL,
    [COD_CREDITO] VARCHAR(20) NOT NULL,
    [ID_CREDITO] INT NOT NULL,
    [ID_CLIENTE] INT NOT NULL,
    [TIPO_DOCUMENTO] CHAR(3) NOT NULL,
    [NRO_DOCUMENTO] VARCHAR(15) NOT NULL,
    [NOMBRE_CLIENTE] VARCHAR(150) NOT NULL,
    [SEXO] CHAR(1) NULL,
    [EDAD_CLIENTE] TINYINT NULL,
    [SEGMENTO_CLIENTE] VARCHAR(30) NOT NULL,
    [ID_AGENCIA] SMALLINT NOT NULL,
    [NOMBRE_AGENCIA] VARCHAR(80) NOT NULL,
    [REGION] VARCHAR(50) NOT NULL,
    [ANALISTA] VARCHAR(80) NOT NULL,
    [ID_PRODUCTO] SMALLINT NOT NULL,
    [NOMBRE_PRODUCTO] VARCHAR(80) NOT NULL,
    [TIPO_CREDITO] VARCHAR(40) NOT NULL,
    [MONEDA] CHAR(3) NOT NULL,
    [FECHA_DESEMBOLSO] DATE NOT NULL,
    [MONTO_DESEMBOLSADO] DECIMAL(18,2) NOT NULL,
    [TASA_ANUAL] DECIMAL(9,4) NOT NULL,
    [NRO_CUOTAS] SMALLINT NOT NULL,
    [CUOTAS_PAGADAS] SMALLINT NOT NULL,
    [CUOTAS_VENCIDAS_IMPAGAS] SMALLINT NOT NULL,
    [CUOTAS_PENDIENTES] SMALLINT NOT NULL,
    [SALDO_CAPITAL] DECIMAL(18,2) NOT NULL,
    [CAPITAL_VENCIDO] DECIMAL(18,2) NOT NULL,
    [DIAS_ATRASO] INT NOT NULL,
    [CALIFICACION] VARCHAR(12) NOT NULL,
    [ESTADO_CREDITO] VARCHAR(20) NOT NULL,
    [FECHA_PROXIMO_VENCIMIENTO] DATE NULL,
    [FECHA_CARGA] DATETIME2(0) NOT NULL CONSTRAINT [DF_TB_CREDITO_FECHA_CARGA] DEFAULT (SYSDATETIME()),
    CONSTRAINT [PK_TB_CREDITO] PRIMARY KEY CLUSTERED ([FECHA_CORTE], [COD_CREDITO])
);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Tablón de créditos: una fila por crédito con saldo a la fecha de corte, con todos los atributos de cliente, agencia y producto desnormalizados.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de corte de la foto de cartera (fin de mes).',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'FECHA_CORTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Código de negocio del crédito.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'COD_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador interno del crédito en el core.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'ID_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador interno del cliente.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'ID_CLIENTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Tipo de documento del cliente.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'TIPO_DOCUMENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Número de documento del cliente.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'NRO_DOCUMENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Apellidos y nombres del cliente.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'NOMBRE_CLIENTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Sexo del cliente.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'SEXO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Edad del cliente en años cumplidos a la fecha de corte.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'EDAD_CLIENTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Segmento comercial del cliente.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'SEGMENTO_CLIENTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador de la agencia.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'ID_AGENCIA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Nombre de la agencia que originó el crédito.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'NOMBRE_AGENCIA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Región de la agencia.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'REGION';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Analista de créditos responsable.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'ANALISTA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador del producto.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'ID_PRODUCTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Nombre comercial del producto.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'NOMBRE_PRODUCTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Tipo de crédito regulatorio.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'TIPO_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Moneda del crédito.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'MONEDA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de desembolso.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'FECHA_DESEMBOLSO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Monto desembolsado.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'MONTO_DESEMBOLSADO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Tasa efectiva anual pactada, en porcentaje.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'TASA_ANUAL';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Número de cuotas pactadas.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'NRO_CUOTAS';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Cuotas pagadas hasta la fecha de corte.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'CUOTAS_PAGADAS';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Cuotas con vencimiento anterior a la fecha de corte que no están pagadas.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'CUOTAS_VENCIDAS_IMPAGAS';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Cuotas no pagadas (vencidas + por vencer).',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'CUOTAS_PENDIENTES';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Saldo de capital a la fecha de corte (capital de cuotas no pagadas).',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'SALDO_CAPITAL';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Capital de cuotas vencidas e impagas.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'CAPITAL_VENCIDO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Días de atraso: días desde el vencimiento de la cuota impaga más antigua.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'DIAS_ATRASO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Calificación por días de atraso: NORMAL, CPP, DEFICIENTE, DUDOSO, PERDIDA.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'CALIFICACION';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Estado contable simplificado: VIGENTE, VENCIDO (más de 30 días de atraso).',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'ESTADO_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Vencimiento de la próxima cuota por vencer; NULL si no quedan cuotas por vencer.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'FECHA_PROXIMO_VENCIMIENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha y hora de carga del registro.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CREDITO',
    @level2type = N'COLUMN', @level2name = N'FECHA_CARGA';
GO
