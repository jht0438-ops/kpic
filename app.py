"""대한유화 FP&A: 공시 실적과 시장가격 지표를 구분한 스프레드·매입시차 분석."""
import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='대한유화 | 스프레드·매입시차 FP&A', page_icon='📈', layout='wide')
st.markdown('''<style>.block-container{max-width:1260px;padding-top:1.6rem}div[data-testid="stMetric"]{background:#f4f7fb;border:1px solid #dce5f0;border-radius:12px;padding:15px}.note{background:#eef4fc;border-radius:12px;padding:15px}</style>''',unsafe_allow_html=True)

# 단위: 원. 대한유화 2026.08.14 반기보고서 p.44 연결 포괄손익계산서
H1={'매출액':1803360563654,'매출원가':1695963696087,'판매비와관리비':37710819835,'영업이익':69686047732}
Q2={'매출액':956254316742,'매출원가':941835714651,'판매비와관리비':18295128812,'영업이익':-3876526721}
Q1={k:H1[k]-Q2[k] for k in H1}
EOK=100_000_000
ACT=pd.DataFrame([{'분기':'2026 1Q',**{k:v/EOK for k,v in Q1.items()}},
                  {'분기':'2026 2Q',**{k:v/EOK for k,v in Q2.items()}}]).set_index('분기')

# 시장가격은 사용자 CSV 업로드가 기본이며 아래는 교육용 가상 예시임.
EXAMPLE=pd.DataFrame({'month':pd.date_range('2025-10-01',periods=12,freq='MS'),
                      'naphtha_usd_t':[605,610,630,640,660,655,625,580,545,565,585,595],
                      'ethylene_usd_t':[850,845,860,900,915,885,830,785,755,780,805,810]})

def normalize_price_csv(upload):
    data=pd.read_csv(upload,encoding='utf-8-sig')
    needed={'month','naphtha_usd_t','ethylene_usd_t'}
    if not needed.issubset(data.columns):
        raise ValueError('필수 열: month, naphtha_usd_t, ethylene_usd_t')
    data=data[list(needed)].copy()
    data['month']=pd.to_datetime(data['month'],errors='coerce').dt.to_period('M').dt.to_timestamp()
    for c in ['naphtha_usd_t','ethylene_usd_t']:
        data[c]=pd.to_numeric(data[c],errors='coerce')
    if data.isna().any().any():
        raise ValueError('날짜나 가격에 빈 값 또는 숫자가 아닌 값이 있습니다.')
    if (data[['naphtha_usd_t','ethylene_usd_t']]<=0).any().any():
        raise ValueError('가격은 0보다 커야 합니다.')
    if data['month'].duplicated().any():
        raise ValueError('동일한 월이 중복되어 있습니다. 월별 한 행만 입력하세요.')
    data=data.sort_values('month').reset_index(drop=True)
    if len(data)<3:
        raise ValueError('최소 3개월의 가격 자료가 필요합니다.')
    # 누락 월이 있으면 과거 가격의 위치를 잘못 연결하므로 차단
    expected=pd.period_range(data['month'].min(),data['month'].max(),freq='M')
    if len(expected)!=len(data):
        raise ValueError('중간에 누락된 월이 있습니다. 연속된 월별 자료를 사용하세요.')
    return data

def enrich(data,lag):
    d=data.copy()
    d['동월 가격차']=d['ethylene_usd_t']-d['naphtha_usd_t']
    d['과거 나프타 가격']=d['naphtha_usd_t'].shift(lag)
    d['시차 적용 가격차']=d['ethylene_usd_t']-d['과거 나프타 가격']
    d['시차 효과']=d['시차 적용 가격차']-d['동월 가격차']
    return d

def plot_series(d,columns,title,ytitle='USD/톤'):
    fig=go.Figure()
    for col in columns:
        fig.add_trace(go.Scatter(x=d['month'],y=d[col],name=col,mode='lines+markers',connectgaps=False))
    fig.update_layout(title=title,height=360,hovermode='x unified',yaxis_title=ytitle,margin=dict(l=20,r=20,t=50,b=20),legend=dict(orientation='h',y=-0.25))
    st.plotly_chart(fig,use_container_width=True)

def conclusion(text):
    st.markdown('#### 이 탭을 통해 얻을 수 있는 결론은 무엇인가요?')
    st.info(text)

st.title('대한유화 | 원재료 매입시차·제품 스프레드 분석')
st.caption('2026년 공시 손익 분석 → 시장가격 비교 → 원재료 매입시차 효과 → 종합 진단')

with st.sidebar:
    st.header('시장가격 데이터')
    uploaded=st.file_uploader('월별 가격 CSV 업로드',type='csv',help='month, naphtha_usd_t, ethylene_usd_t')
    if uploaded:
        try:
            PRICES=normalize_price_csv(uploaded)
            source='사용자 업로드 데이터 (출처·시장·가격 기준은 사용자가 검증해야 함)'
            st.success(f'{len(PRICES)}개월 자료를 불러왔습니다.')
        except Exception as exc:
            st.error(str(exc))
            st.stop()
    else:
        PRICES=EXAMPLE.copy()
        source='가상 예시 데이터 (실제 시장가격 아님)'
        st.warning('현재는 가상 예시 가격입니다. 실제 가격을 분석하려면 CSV를 업로드하세요.')
    st.download_button('CSV 입력 양식 다운로드',data=pd.DataFrame({'month':['2026-01','2026-02','2026-03'],'naphtha_usd_t':['','',''],'ethylene_usd_t':['','','']}).to_csv(index=False).encode('utf-8-sig'),file_name='monthly_prices_template.csv',mime='text/csv')
    st.caption('두 가격은 반드시 같은 지역·시장 기준의 USD/톤 시계열을 사용하세요. 예: 동북아 나프타·에틸렌 월평균 지표.')
    lag=st.select_slider('원재료 가격 반영 시차 (개월)',options=[0,1,2,3],value=1)
    st.caption('시차는 공시로 확인된 실제 재고회전기간이 아닌 분석 가정입니다.')
    st.divider()
    st.markdown('**자료 출처**')
    st.caption('대한유화 2026.08.14 반기보고서 p.44 연결 포괄손익계산서, p.17~19 제품·원재료 설명; 2026.03.05 사업보고서; 첨부 심층분석보고서. 월별 시장가격은 별도 업로드.')

D=enrich(PRICES,lag)
valid=D.dropna(subset=['시차 적용 가격차']).copy()
mode='실제 시장가격 업로드' if uploaded else '가상 예시'
if not uploaded:
    st.warning('**데이터 상태: 가상 예시.** 화면의 월별 가격과 가격차·시차 효과는 실제 대한유화나 시장의 수치가 아닙니다.')

intro,real,spread,lagtab,summary=st.tabs(['① 개요','② 실제 실적 분석','③ 나프타·에틸렌 스프레드','④ 원재료 매입시차','⑤ 종합 진단'])
with intro:
    st.subheader('이 프로그램은 무엇인가요?')
    st.write('대한유화의 2026년 1·2분기 실제 영업실적을 비교하고, 나프타와 에틸렌의 월별 가격차 및 **원재료 매입·원가 반영 시차**가 가격차 지표에 미치는 영향을 살펴보는 FP&A 분석 도구입니다.')
    st.markdown('''**왜 만들었나요?** 2026년 2분기는 매출이 증가했지만 영업이익이 감소했습니다. 단순히 나프타 가격만으로 이 현상을 설명할 수는 없습니다. 원재료를 어느 시점에 매입했는지, 제품가격은 얼마나 변했는지, 매출원가가 얼마나 증가했는지를 구분할 필요가 있습니다.''')
    st.markdown('**사용 순서**')
    st.markdown('''1. **실제 실적 분석:** 공시를 통해 매출·매출원가·판관비가 영업이익에 미친 회계상 영향을 확인합니다.
2. **스프레드 분석:** 월별 나프타와 에틸렌 시장가격이 함께 움직였는지 비교합니다.
3. **매입시차 분석:** 0~3개월 시차를 바꿔 같은 달 제품가격과 과거 원료가격의 차이를 비교합니다.
4. **종합 진단:** 시장가격 신호와 실제 손익을 함께 읽고, 추가로 확인해야 할 원인을 정리합니다.''')
    st.markdown('**데이터의 의미**')
    st.write('① 공시 재무수치 = 대한유화 연결 실적. ② 업로드한 시장가격 = 회사의 실제 계약가격이 아닌 외부 가격지표. ③ 시차 적용 가격차 = 단순화된 가격차 지표로, 실제 제품별 공헌이익이나 영업이익이 아닙니다.')
    st.warning('NCC는 에틸렌 외에도 여러 제품을 동시에 생산합니다. 이 도구는 나프타 1톤이 에틸렌 1톤으로 바뀐다는 뜻이 아니며, 제조수율·결합원가·재고평가손익을 추정하지 않습니다.')

with real:
    st.subheader('2026년 1분기와 2분기: 무엇이 달라졌나?')
    st.caption('실제 공시 수치 · 연결 기준 · 억 원. 1분기는 상반기 누적에서 2분기 3개월 수치를 차감.')
    delta=ACT.iloc[1]-ACT.iloc[0]
    a,b,c=st.columns(3)
    a.metric('2분기 매출액',f'{ACT.iloc[1]["매출액"]:,.1f}억',f'{delta["매출액"]:+,.1f}억')
    b.metric('2분기 영업이익',f'{ACT.iloc[1]["영업이익"]:,.1f}억',f'{delta["영업이익"]:+,.1f}억')
    c.metric('2분기 매출원가',f'{ACT.iloc[1]["매출원가"]:,.1f}억',f'{delta["매출원가"]:+,.1f}억')
    st.dataframe(ACT.style.format('{:,.1f}'),use_container_width=True)
    steps=['1Q 영업이익','매출 증가 효과','매출원가 증가 효과','판관비 변화 효과','2Q 영업이익']
    vals=[ACT.iloc[0]['영업이익'],delta['매출액'],-delta['매출원가'],-delta['판매비와관리비'],ACT.iloc[1]['영업이익']]
    fig=go.Figure(go.Waterfall(x=steps,y=vals,measure=['absolute','relative','relative','relative','total'],text=[f'{v:+,.1f}' for v in vals],textposition='outside'))
    fig.update_layout(title='영업이익 변동 브리지 (회계 항목별 증감)',height=440,yaxis_title='억 원')
    st.plotly_chart(fig,use_container_width=True)
    excess=delta['매출원가']-delta['매출액']
    conclusion(f'2분기에는 매출액이 {delta["매출액"]:,.1f}억 원 늘었지만, 매출원가가 {delta["매출원가"]:,.1f}억 원 증가했습니다. '
               f'즉 **매출원가 증가액이 매출 증가액을 {excess:,.1f}억 원 초과**했습니다. '
               f'판관비 변화({delta["판매비와관리비"]:+,.1f}억 원)까지 반영한 영업이익 변동은 {delta["영업이익"]:+,.1f}억 원입니다. '
               '이는 **회계 항목별 감소 요인**이며, 매출원가 증가분을 나프타 가격·판매량·재고효과 등으로 확정 분해한 결과는 아닙니다.')

with spread:
    st.subheader('월별 나프타·에틸렌 가격과 단순 스프레드')
    st.caption(f'데이터: {source} · USD/톤 · 동월 가격차 = 에틸렌 가격 − 나프타 가격')
    plot_series(D.rename(columns={'naphtha_usd_t':'나프타 가격','ethylene_usd_t':'에틸렌 가격'}),['나프타 가격','에틸렌 가격'],'원재료와 제품의 가격 움직임')
    plot_series(D,['동월 가격차'],'동월 에틸렌−나프타 단순 가격차')
    last=D.iloc[-1]
    prev=D.iloc[-2]
    x,y,z=st.columns(3)
    x.metric('최근 월 나프타',f'{last["naphtha_usd_t"]:,.0f} USD/t',f'{last["naphtha_usd_t"]-prev["naphtha_usd_t"]:+,.0f}')
    y.metric('최근 월 에틸렌',f'{last["ethylene_usd_t"]:,.0f} USD/t',f'{last["ethylene_usd_t"]-prev["ethylene_usd_t"]:+,.0f}')
    z.metric('최근 월 단순 가격차',f'{last["동월 가격차"]:,.0f} USD/t',f'{last["동월 가격차"]-prev["동월 가격차"]:+,.0f}')
    sdelta=last['동월 가격차']-prev['동월 가격차']
    conclusion(f'가장 최근 월의 동월 가격차는 {last["동월 가격차"]:,.0f} USD/톤이며 전월보다 {abs(sdelta):,.0f} USD/톤 '
               f'{"확대" if sdelta>0 else "축소" if sdelta<0 else "유지"}됐습니다. '
               '나프타 가격이 하락해도 에틸렌 가격이 더 빠르게 하락하면 가격차는 축소될 수 있습니다. '
               +('단, 현재 가격은 **가상 예시**이므로 실제 업황 판단에는 사용할 수 없습니다.' if not uploaded else '이는 업로드한 시장가격 지표에 관한 해석으로, 대한유화의 실제 제조마진과는 다릅니다.'))
    st.dataframe(D[['month','naphtha_usd_t','ethylene_usd_t','동월 가격차']].rename(columns={'month':'월','naphtha_usd_t':'나프타 USD/t','ethylene_usd_t':'에틸렌 USD/t'}).style.format({'나프타 USD/t':'{:,.0f}','에틸렌 USD/t':'{:,.0f}','동월 가격차':'{:,.0f}'}),use_container_width=True,hide_index=True)

with lagtab:
    st.subheader('원재료 매입 시차가 가격차에 미치는 영향')
    st.markdown(f'**시뮬레이션 질문:** 제품은 이번 달 가격으로 판매하고 원재료 가격은 **{lag}개월 전 가격**을 적용한다면, 동월 가격차와 얼마나 달라질까요?')
    st.caption('매입 시점과 실제 원가 인식 시점이 일치한다는 가정의 단순 가격차 분석. 실제 재고평가손익·회계상 매출원가 계산이 아님.')
    plot_series(D,['동월 가격차','시차 적용 가격차'],'동월 가격차 vs 시차 적용 가격차')
    plot_series(D,['시차 효과'],'시차 효과 = 시차 적용 가격차 − 동월 가격차')
    if valid.empty:
        st.warning('시차를 적용할 수 있는 월이 없습니다. 데이터를 더 추가해 주세요.')
    else:
        last=valid.iloc[-1]
        x,y,z=st.columns(3)
        x.metric('최근 월 동월 가격차',f'{last["동월 가격차"]:,.0f} USD/t')
        y.metric('최근 월 시차 적용 가격차',f'{last["시차 적용 가격차"]:,.0f} USD/t')
        z.metric('최근 월 시차 효과',f'{last["시차 효과"]:+,.0f} USD/t')
        eff=last['시차 효과']
        conclusion(f'{lag}개월 시차를 가정하면 최근 월의 가격차는 동월 기준보다 {abs(eff):,.0f} USD/톤 '
                   f'{"높아집니다" if eff>0 else "낮아집니다" if eff<0 else "같습니다"}. '
                   '이는 과거 원료가격과 현재 원료가격의 차이에서 발생한 **단순 가격차 효과**입니다. '
                   +('가상 데이터이므로 실제 기업의 래깅·역래깅 실적이라고 해석하면 안 됩니다.' if not uploaded else '실제 구매 시점, 재고 소진, 생산수율, 제품 믹스가 다르면 회사의 실현 손익은 달라집니다.'))
        st.dataframe(valid[['month','ethylene_usd_t','naphtha_usd_t','과거 나프타 가격','동월 가격차','시차 적용 가격차','시차 효과']].rename(columns={'month':'월','ethylene_usd_t':'에틸렌 USD/t','naphtha_usd_t':'동월 나프타 USD/t'}).style.format(precision=1),use_container_width=True,hide_index=True)
        st.download_button('시차 분석 CSV 다운로드',valid.to_csv(index=False).encode('utf-8-sig'),file_name='kpic_lag_analysis.csv',mime='text/csv')

with summary:
    st.subheader('종합 진단: 가격 신호와 실제 손익을 함께 읽기')
    delta=ACT.iloc[1]-ACT.iloc[0]
    st.markdown('**1. 실제 재무성과에서 확인된 사실**')
    st.write(f'2026년 2분기 연결 매출은 전분기 대비 {delta["매출액"]:+,.1f}억 원, 매출원가는 {delta["매출원가"]:+,.1f}억 원, 영업이익은 {delta["영업이익"]:+,.1f}억 원 변했습니다. 매출원가 증가가 매출 증가를 상회한 것이 영업이익 악화의 회계상 핵심 요인입니다.')
    st.markdown('**2. 가격·시차 지표에서 확인할 수 있는 내용**')
    st.write(f'현재 데이터는 **{mode}**이며, 시차 가정은 **{lag}개월**입니다. 시장가격 자료를 통해 원재료와 제품가격의 상대적 움직임, 과거 원료가격 적용 시 가격차 변화 방향을 확인할 수 있습니다.')
    st.markdown('**3. 추가로 확인해야 실제 원인을 판단할 수 있는 항목**')
    st.markdown('''- 실제 나프타 매입단가와 재고 소진 시점
- 에틸렌 외 프로필렌·PE·PP 등 제품별 판매량·판매가격과 결합원가
- 재고자산평가손익 및 생산·판매량, 가동률, 환율
- 연결 자회사 한주 등 화학사업 외 부문의 실적 영향''')
    conclusion('**확정 가능한 결론:** 공시상 매출원가 증가가 매출 증가를 웃돌면서 2026년 2분기 연결 영업이익이 감소했습니다. '
               '**검토할 가설:** 원재료·제품가격의 움직임과 원가 반영 시차가 화학사업의 수익성 변동에 영향을 주었을 수 있습니다. '
               '다만 시장가격차는 실제 매입·판매가격과 제품별 원가를 대신하지 못하므로, **영업이익 감소액 중 나프타 시차 효과가 몇 억 원인지 이 프로그램만으로 확정할 수 없습니다.**')
    st.markdown('---')
    st.caption('자료 기준: 대한유화 반기보고서(2026.08.14) 연결 포괄손익계산서 p.44. 가격·시차 지표는 업로드 자료 또는 가상 예시이며 공시 실적과 직접 회귀·인과 추정하지 않았습니다.')
