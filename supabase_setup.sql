-- SQL para criar a tabela no Supabase
-- Execute este SQL no SQL Editor do Supabase (https://supabase.com/dashboard)

-- Criar tabela de resultados
CREATE TABLE IF NOT EXISTS resultados (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    loteria TEXT NOT NULL,
    horario TEXT NOT NULL,
    grupo INTEGER NOT NULL,
    centena INTEGER NOT NULL,
    milhar INTEGER NOT NULL,
    animal TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    
    -- Constraint para evitar duplicatas
    UNIQUE(data, loteria, horario, milhar)
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_resultados_loteria ON resultados(loteria);
CREATE INDEX IF NOT EXISTS idx_resultados_data ON resultados(data);
CREATE INDEX IF NOT EXISTS idx_resultados_loteria_data ON resultados(loteria, data);

-- Habilitar RLS (Row Level Security)
ALTER TABLE resultados ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura pública
CREATE POLICY "Allow public read" ON resultados
    FOR SELECT USING (true);

-- Política para permitir inserção pública  
CREATE POLICY "Allow public insert" ON resultados
    FOR INSERT WITH CHECK (true);

-- Política para permitir atualização pública
CREATE POLICY "Allow public update" ON resultados
    FOR UPDATE USING (true);
