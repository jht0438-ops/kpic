"""대한유화 FP&A 실적 분석 및 나프타 가격 민감도 (Streamlit)."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title='대한유화 손익 분석', page_icon='📊', layout='wide')
st.markdown('''<style>
.block-container {max-width:1200px;padding-top:2rem}
[data-testid="stMetric"] {background:#f5f7fa;border:1px solid #e3e8ef;border-radius:12px;padding:15px}
</style>''', unsafe_allow_html=True)

# 연결 포괄손익계산서, 2026년 반기보고서 p.44 (원 단위)
H1 = {'매출액':1803360563654,'매출원가':1695963696087,
      '판매비와관리비':37710819835,'영업이익':69686047732}
Q2 = {'매출액':956254316742,'매출원가':941835714651,
      '판매비와관리비':18295128812,'영업이익':-3876526721}
Q1 = {k:H1[k]-Q2[k] for k in H1}
assert all(d['매출액']-d['매출원가']-d['판매비와관리비']==d['영업이익'] for d in [H1,Q1,Q2])
TO_EOK=100_000_000
real=pd.DataFrame({'2026년 1분기':Q1,'2026년 2분기':Q2}).T / TO_EOK
real['영업이익률(%)']=real['영업이익']/real['매출액']*100
before,after=real.iloc[0],real.iloc[1]
d_sales=after['매출액']-before['매출액']
d_cogs=after['매출원가']-before['매출원가']
d_sga=after['판매비와관리비']-before['판매비와관리비']
d_op=after['영업이익']-before['영업이익']

st.title('대한유화 | 손익 변동 분석 및 전망')
st.caption('2026년 1·2분기 연결 실적 · 금액 단위: 억 원')
intro,history,forecast=st.tabs(['① 개요','② 실적 분석','③ 나프타 가격 분석'])

with intro:
    st.header('이 프로그램은 무엇인가요?')
    st.write('대한유화의 **실제 영업이익 변동을 재무제표 항목별로 분석**하고, '
             '**나프타 가격 변화가 향후 영업이익에 미칠 수 있는 영향**을 가정에 따라 살펴보는 FP&A 분석 프로그램입니다.')
    st.info('**분석의 출발점** 2026년 2분기에는 전분기보다 매출이 증가했지만 영업이익은 감소했습니다. '
            '왜 이런 일이 발생했는지 확인하고, 원재료 가격이 바뀌면 손익이 어떻게 달라질지 검토합니다.')
    st.subheader('어떻게 사용하나요?')
    a,b=st.columns(2)
    with a:
        st.markdown('**1단계 | 실적 분석**')
        st.write('2026년 1분기와 2분기 공시 수치를 비교합니다. 매출 증가 효과와 매출원가·판관비 증가 부담을 '
                 '구분하여 영업이익이 왜 감소했는지 확인합니다.')
    with b:
        st.markdown('**2단계 | 나프타 가격 분석**')
        st.write('나프타 가격 변동률 하나만 조정합니다. 다른 조건을 고정한 단순 가정 아래 '
                 '예상 영업이익이 어떻게 변하는지 수치와 그래프로 확인합니다.')
    st.subheader('분석할 때 주의할 점')
    st.write('**실적 분석은 공시자료에 기반한 회계적 증감 분석**입니다. 반면 **나프타 가격 분석은 '
             '가정에 따른 민감도 분석**으로, 회사의 실제 나프타 매입단가·투입량을 활용한 예측이 아닙니다. '
             '두 결과를 혼동하지 않도록 구분해 표시했습니다.')
    st.caption('실적 출처: 대한유화 반기보고서(2026.08.14), 연결 포괄손익계산서(p.44). '
               '1분기는 반기 누적에서 2분기(3개월)를 차감하여 계산했습니다.')

with history:
    st.header('2026년 1분기 vs 2분기 실적')
    a,b,c=st.columns(3)
    a.metric('2분기 매출액',f'{after["매출액"]:,.1f}억',f'{d_sales:+,.1f}억 (전분기 대비)')
    b.metric('2분기 영업이익',f'{after["영업이익"]:,.1f}억',f'{d_op:+,.1f}억 (전분기 대비)')
    c.metric('2분기 영업이익률',f'{after["영업이익률(%)"]:.2f}%',
             f'{after["영업이익률(%)"]-before["영업이익률(%)"]:+.2f}%p')
    st.dataframe(real.T.style.format('{:,.2f}'),use_container_width=True)
    st.subheader('영업이익이 어떻게 변했나요?')
    bridge_labels=['1분기 영업이익','매출 증가 효과','매출원가 증가 부담','판관비 증감 효과','2분기 영업이익']
    bridge_values=[before['영업이익'],d_sales,-d_cogs,-d_sga,after['영업이익']]
    fig=go.Figure(go.Waterfall(x=bridge_labels,y=bridge_values,
        measure=['absolute','relative','relative','relative','total'],
        text=[f'{x:+,.1f}' for x in bridge_values],textposition='outside'))
    fig.update_layout(height=440,yaxis_title='억 원',showlegend=False,
                      margin=dict(l=30,r=30,t=25,b=20))
    st.plotly_chart(fig,use_container_width=True)
    st.subheader('이 탭을 통해 얻을 수 있는 결론은 무엇인가요?')
    st.success(f'2026년 2분기 매출액은 전분기보다 **{d_sales:,.1f}억 원 증가**했지만, '
               f'매출원가는 **{d_cogs:,.1f}억 원 증가**했습니다. '
               f'판매비와관리비는 **{d_sga:,.1f}억 원 변동**하여, '
               f'결과적으로 영업이익은 **{abs(d_op):,.1f}억 원 감소**했습니다.')
    if d_cogs>d_sales:
        st.write(f'즉, **매출 증가 효과보다 매출원가 증가 부담이 {d_cogs-d_sales:,.1f}억 원 더 컸던 점**이 '
                 '영업이익 감소를 설명하는 핵심적인 회계상 요인입니다.')
    st.caption('주의: 이 탭은 재무제표 항목의 증감을 설명합니다. 매출원가 증가 중 나프타 가격·재고효과·'
               '판매량·환율·사업별 영향이 각각 얼마인지는 공시만으로 확정할 수 없습니다.')
    st.caption('출처: 대한유화 2026년 반기보고서, 연결 포괄손익계산서(p.44).')

with forecast:
    st.header('나프타 가격 변화에 따른 영업이익 시뮬레이션')
    st.write('**무엇을 시뮬레이션하나요?** 2026년 2분기 영업이익을 기준으로, '
             '**나프타 가격만 변하고 판매가격·판매량·기타 비용은 그대로**라고 가정할 때 '
             '영업이익이 얼마나 달라지는지 계산합니다.')
    # 교육용 가정. 기업 공시로 확인된 나프타 원가 비중이 아님.
    ASSUMED_EXPOSURE=0.45
    exposed_cost=after['매출원가']*ASSUMED_EXPOSURE
    st.warning('**핵심 가정(공시 사실 아님):** 2분기 매출원가의 **45%**가 나프타 가격에 '
               '동일한 비율로 반응한다고 가정합니다. 가격 변동은 분석 기간의 원가에 전액 반영되며 '
               '판매가격·판매량은 변하지 않는 것으로 단순화합니다. '
               '실제 원료 비중과 매입·판매 시차, 재고평가손익은 확인되지 않아 반영하지 않았습니다.')
    pct=st.slider('나프타 가격 변동률 (%)',min_value=-30,max_value=30,value=10,step=5)
    impact=-exposed_cost*pct/100
    expected=after['영업이익']+impact
    a,b,c=st.columns(3)
    a.metric('기준: 실제 2분기 영업이익',f'{after["영업이익"]:,.1f}억')
    b.metric('가정상 영업이익 변화',f'{impact:+,.1f}억')
    c.metric('가정상 예상 영업이익',f'{expected:,.1f}억')
    scenarios=pd.DataFrame({'나프타 가격 변동률(%)':list(range(-30,31,5))})
    scenarios['가정상 예상 영업이익(억 원)']=after['영업이익']-exposed_cost*scenarios['나프타 가격 변동률(%)']/100
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=scenarios.iloc[:,0],y=scenarios.iloc[:,1],mode='lines+markers',
                             name='가정상 영업이익'))
    fig.add_trace(go.Scatter(x=[pct],y=[expected],mode='markers+text',
                             text=[f'{expected:,.1f}억'],textposition='top center',
                             marker=dict(size=14),name='선택한 시나리오'))
    fig.add_hline(y=0,line_dash='dash',annotation_text='손익분기선')
    fig.update_layout(height=420,xaxis_title='나프타 가격 변동률(%)',yaxis_title='예상 영업이익(억 원)',
                      legend_orientation='h',margin=dict(l=30,r=30,t=35,b=20))
    st.plotly_chart(fig,use_container_width=True)
    st.subheader('이 탭을 통해 얻을 수 있는 결론은 무엇인가요?')
    if pct>0:
        st.success(f'나프타 가격이 **{pct}% 상승**하면, 설정한 단순 가정 아래 원가 부담이 '
                   f'**{abs(impact):,.1f}억 원 증가**해 영업이익이 '
                   f'**{after["영업이익"]:,.1f}억 원에서 {expected:,.1f}억 원으로 감소**합니다.')
    elif pct<0:
        st.success(f'나프타 가격이 **{abs(pct)}% 하락**하면, 설정한 단순 가정 아래 원가 부담이 '
                   f'**{impact:,.1f}억 원 감소**해 영업이익이 '
                   f'**{after["영업이익"]:,.1f}억 원에서 {expected:,.1f}억 원으로 개선**됩니다.')
    else:
        st.success(f'나프타 가격이 변하지 않으면, 가정상 영업이익은 기준 실적 '
                   f'**{expected:,.1f}억 원**과 같습니다.')
    st.write('**해석:** 나프타 가격 변동이 제품가격에 전가되지 않는다면 원재료비 부담이 손익을 '
             '악화시키거나 개선할 수 있습니다. 따라서 손익 전망에서는 원재료 가격 변화뿐 아니라 '
             '실제 원료 투입 비중, 제품 판매가격, 재고 및 매입·판매 시차도 함께 확인해야 합니다.')
    with st.expander('계산식과 시나리오 표 확인'):
        st.latex(r'\text{가상 손익변화}=-\text{2분기 매출원가}\times 45\%\times\text{나프타 가격변동률}')
        st.latex(r'\text{가상 예상 영업이익}=\text{2분기 실제 영업이익}+\text{가상 손익변화}')
        st.dataframe(scenarios.style.format({'가정상 예상 영업이익(억 원)':'{:,.1f}'}),
                     use_container_width=True,hide_index=True)
    st.caption('시뮬레이션은 교육용 민감도 예시이며, 대한유화의 실제 원가구조나 향후 실적 전망이 아닙니다.')
