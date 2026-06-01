import streamlit as st

def render():
    st.html("""
    <style>
    .premio-card {
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .premio-1 { background: linear-gradient(135deg, #FFF8DC, #FFE066); border: 2px solid #F5C518; }
    .premio-2 { background: linear-gradient(135deg, #F5F5F5, #E0E0E0); border: 2px solid #A8A9AD; }
    .premio-3 { background: linear-gradient(135deg, #FFF0E6, #FFD4B0); border: 2px solid #C07A3A; }
    .premio-emoji { font-size: 3rem; }
    .premio-lugar { font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; color: #003087; }
    .premio-desc { font-size: 1.1rem; font-weight: 600; color: #1A202C; }
    .premio-sub  { font-size: 13px; color: #718096; margin-top: 2px; }

    .regla-section {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        border: 1px solid #E2E8F0;
    }
    .regla-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.2rem;
        color: #003087;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .pts-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0;
        border-bottom: 1px solid #F0F4F8;
        font-size: 15px;
    }
    .pts-row:last-child { border-bottom: none; }
    .pts-badge {
        background: #003087;
        color: white;
        border-radius: 6px;
        padding: 3px 10px;
        font-weight: 700;
        font-size: 14px;
        min-width: 48px;
        text-align: center;
    }
    .pts-badge-gold   { background: #F5C518; color: #000; }
    .pts-badge-green  { background: #00B37D; color: #fff; }
    .pts-badge-gray   { background: #CBD5E0; color: #4A5568; }
    .pts-badge-blue   { background: #003087; color: #fff; }
    </style>

    <!-- HEADER -->
    <div style="text-align:center; margin-bottom:28px;">
        <div style="font-size:3.5rem;">🏆</div>
        <h1 style="font-family:'Bebas Neue',sans-serif; font-size:2.4rem;
                   color:#003087; letter-spacing:2px; margin:4px 0;">
            REGLAS Y PREMIOS
        </h1>
        <p style="color:#718096; font-size:14px;">
            Quiniela Mundial 2026 &nbsp;·&nbsp; Danone México &nbsp;·&nbsp; Mérida, Yucatán
        </p>
    </div>

    <!-- PREMIOS -->
    <div class="regla-section">
        <div class="regla-title">🎁 Premios</div>

        <div class="premio-card premio-1">
            <div class="premio-emoji">🥇</div>
            <div>
                <div class="premio-lugar">1er Lugar</div>
                <div class="premio-desc">Tarjeta de regalo $1,500</div>
                <div class="premio-sub">+ Souvenir exclusivo del Mundial 2026 ⚽</div>
            </div>
        </div>

        <div class="premio-card premio-2">
            <div class="premio-emoji">🥈</div>
            <div>
                <div class="premio-lugar">2do Lugar</div>
                <div class="premio-desc">Tarjeta de regalo $1,000</div>
            </div>
        </div>

        <div class="premio-card premio-3">
            <div class="premio-emoji">🥉</div>
            <div>
                <div class="premio-lugar">3er Lugar</div>
                <div class="premio-desc">Tarjeta de regalo $600</div>
            </div>
        </div>
    </div>

    <!-- PUNTUACIÓN GRUPOS -->
    <div class="regla-section">
        <div class="regla-title">⚽ Puntuación — Fase de Grupos (Jun 11 – Jun 27)</div>
        <div class="pts-row">
            <span class="pts-badge pts-badge-gold">3 pts</span>
            <span>Resultado exacto (ej. pronosticas 2-1 y termina 2-1)</span>
        </div>
        <div class="pts-row">
            <span class="pts-badge pts-badge-green">1 pt</span>
            <span>Aciertas ganador o empate (ej. pronosticas 2-1 y termina 3-0)</span>
        </div>
        <div class="pts-row">
            <span class="pts-badge pts-badge-gray">0 pts</span>
            <span>Pronóstico incorrecto</span>
        </div>
    </div>

    <!-- PUNTUACIÓN ELIMINATORIAS -->
    <div class="regla-section">
        <div class="regla-title">🔥 Puntuación — Eliminatorias (Ronda de 32 hasta Final)</div>
        <p style="color:#718096; font-size:13px; margin-bottom:12px;">
            En eliminatorias solo eliges <b>quién avanza</b> a la siguiente ronda —
            sin importar el marcador ni si hay prórroga o penales.
        </p>
        <div class="pts-row">
            <span class="pts-badge pts-badge-blue">2 pts</span>
            <span>Aciertas qué equipo pasa a la siguiente ronda</span>
        </div>
        <div class="pts-row">
            <span class="pts-badge pts-badge-gray">0 pts</span>
            <span>Pronóstico incorrecto</span>
        </div>
    </div>

    <!-- PARTICIPACIÓN -->
    <div class="regla-section">
        <div class="regla-title">📋 Participación</div>
        <div class="pts-row">🎟️ <span>Entrada <b>gratuita</b> para todos los colaboradores de Danone Mérida</span></div>
        <div class="pts-row">⏰ <span>Los pronósticos se <b>bloquean automáticamente</b> al inicio de cada partido</span></div>
        <div class="pts-row">📅 <span>El torneo abarca del <b>11 de junio al 19 de julio 2026</b></span></div>
        <div class="pts-row">🏅 <span>Gana quien acumule <b>más puntos al terminar la Final</b></span></div>
        <div class="pts-row">📵 <span>Si no pronosticas un partido antes de que inicie, ese partido vale <b>0 pts</b></span></div>
    </div>

    <!-- DESEMPATE -->
    <div class="regla-section">
        <div class="regla-title">⚖️ Criterios de Desempate</div>
        <div class="pts-row">🥇 <span>1° Mayor número de <b>resultados exactos</b> en fase de grupos</span></div>
        <div class="pts-row">🥈 <span>2° Mayor número de <b>partidos pronosticados</b></span></div>
        <div class="pts-row">🎲 <span>3° <b>Sorteo</b> entre empatados</span></div>
    </div>

    <!-- NOTA -->
    <div style="background:#EBF8FF; border-radius:10px; padding:14px 18px;
                border-left:4px solid #0057B8; font-size:13px; color:#2C5282;">
        ⚽ <b>¡Que gane el mejor!</b> Cualquier duda sobre reglas o premios
        comunícate con el área de Recursos Humanos Danone Mérida.
    </div>
    """)