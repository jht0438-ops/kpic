import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='대한유화 생산성·원가차이 통합 분석',page_icon='📊',layout='wide')
st.title('대한유화 생산성·원가차이 통합 분석')
st.caption('생산현황 → 생산량·수율과 단위당 제조원가 → 표준·실제 원가차이 → 경영관리 진단')
st.info('생산능력·생산실적·가동률은 대한유화 공시값입니다. 수율과 모든 원가·표준값·실제값은 사용자 입력 시나리오이며 대한유화 실제 제조원가가 아닙니다.')

rows=[('2023','온산공장',2145000,1721611,80.26),('2023','울산공장',1200000,803713,66.98),('2024','온산공장',2141000,1867008,87.20),('2024','울산공장',1200000,793755,66.15),('2025','온산공장',2141000,1947334,90.95),('2025','울산공장',1200000,787910,65.66),('2026 상반기','온산공장',1070500,756128,70.63),('2026 상반기','울산공장',600000,375068,62.51)]
df=pd.DataFrame(rows,columns=['기간','공장','생산능력','생산실적','공시 가동률(%)'])
df['미활용 생산능력']=df['생산능력']-df['생산실적']

def explain(why,how,result):
 st.markdown('**왜 분석하나요?** '+why)
 st.markdown('**어떻게 분석하나요?** '+how)
 st.markdown('**이 탭에서 얻는 결론은?** '+result)

def num(label,key,value=0.0,step=1.0):
 return st.number_input(label,min_value=0.0,value=float(value),step=float(step),key=key)

def sign(v): return '불리(U)' if v>1e-7 else ('유리(F)' if v< -1e-7 else '차이 없음')

def money(v):return f'{v:+,.0f}원 ({sign(v)})'

t1,t2,t3,t4,t5=st.tabs(['① 실제 생산현황','② 생산량·단위당 원가','③ 수율·통합 시나리오','④ 원가차이 분석','⑤ 종합 진단'])
with t1:
 st.subheader('공시 생산현황 (석유화학 부문)')
 explain('공장별 생산능력 대비 생산실적의 차이가 제조원가에 미칠 수 있는 영향을 확인하기 위해서입니다.','2023~2025년과 2026년 상반기의 공시 생산능력·실적·가동률을 비교합니다.','온산공장과 울산공장은 가동률과 제품군이 다르므로 공장별로 분리해 분석해야 합니다.')
 st.dataframe(df,hide_index=True,use_container_width=True)
 p=st.selectbox('공장 선택',['온산공장','울산공장'],key='p1')
 sub=df[df['공장']==p]
 fig=px.bar(sub,x='기간',y=['생산능력','생산실적'],barmode='group',title='생산능력과 생산실적 (톤)')
 st.plotly_chart(fig,use_container_width=True)
 fig=px.line(sub,x='기간',y='공시 가동률(%)',markers=True,title='공시 가동률 (%)')
 st.plotly_chart(fig,use_container_width=True)
 st.caption('출처: 2023·2024·2025 사업보고서 및 2026 반기보고서, II.3. 원재료 및 생산설비. 2026 상반기는 반기 생산능력으로 비교합니다. 공시 가동률은 공시 원문값을 사용합니다.')
 st.warning('공시상 생산실적은 제품군별 총 생산량입니다. 정상품 수율은 공개되지 않았으며, 생산실적에 별도의 가정 수율을 적용한 값은 회계상 실제 정상품 수량이 아닙니다. 온산공장 기초유분은 연산제품을 동시에 생산하므로 톤당 원가 해석에 한계가 있습니다.')

with t2:
 st.subheader('생산량 변화와 단위당 제조원가')
 explain('생산량이 증가하면 같은 기간 고정제조원가를 더 많은 생산량에 배부할 수 있습니다.','공시된 공장·기간의 생산량을 기준으로 시나리오 생산량과 가정 고정비·변동비를 입력합니다.','가정이 같을 때 생산량이 늘면 톤당 고정비 부담이 낮아지는 효과를 확인합니다.')
 c1,c2=st.columns(2)
 with c1: period=st.selectbox('공시 기준기간',df['기간'].unique(),index=2,key='base_period')
 with c2: plant=st.selectbox('공시 기준공장',['온산공장','울산공장'],key='base_plant')
 base=df[(df['기간']==period)&(df['공장']==plant)].iloc[0]
 cap=float(base['생산능력']); q0=float(base['생산실적'])
 a,b,c=st.columns(3)
 a.metric('공시 생산능력',f'{cap:,.0f}톤');b.metric('공시 생산실적',f'{q0:,.0f}톤');c.metric('공시 가동률',f"{base['공시 가동률(%)']:.2f}%")
 st.markdown('#### 사용자 가정 입력')
 a,b,c=st.columns(3)
 with a: fixed=num('기간 고정제조원가 (억원)','fixed',300,10)
 with b: variable=num('톤당 변동제조원가 (만원/톤)','variable',10,1)
 with c: q1=num('시나리오 생산량 (톤)','q1',q0,1000)
 if q1>cap:st.warning('시나리오 생산량이 해당 기간의 공시 생산능력을 초과합니다. 설비증설 등 별도 전제가 필요합니다.')
 def cost(q,y=100):
  good=q*y/100
  total=fixed*1e8+q*variable*1e4
  return {'정상품 환산량':good,'총 제조원가(억원)':total/1e8,'톤당 제조원가(만원)':total/good/1e4 if good>0 else None,'톤당 고정비(만원)':fixed*1e8/good/1e4 if good>0 else None,'가동률(%)':q/cap*100}
 a0=cost(q0);a1=cost(q1)
 comparison=pd.DataFrame([{'구분':'공시 생산량 기준',**a0},{'구분':'시나리오',**a1}])
 st.dataframe(comparison,hide_index=True,use_container_width=True)
 if a0['톤당 제조원가(만원)'] and a1['톤당 제조원가(만원)']:
  delta=a1['톤당 제조원가(만원)']-a0['톤당 제조원가(만원)']
  st.success(f'톤당 제조원가 변화: {delta:+,.2f}만원/톤 (수율 100% 고정, 가정 원가 기준)')
 samples=[{'생산량(톤)':q,'톤당 제조원가(만원)':cost(q)['톤당 제조원가(만원)']} for q in [cap*x/20 for x in range(1,21)]]
 st.plotly_chart(px.line(pd.DataFrame(samples),x='생산량(톤)',y='톤당 제조원가(만원)',markers=True),use_container_width=True)
 st.caption('고정비는 생산량과 무관하게 일정, 변동비는 톤당 일정한 단순 모형입니다. 공시 생산량 자체를 정상품으로 간주한 100% 수율 기준 비교입니다.')

with t3:
 st.subheader('수율 변화와 생산량을 결합한 통합 시나리오')
 explain('투입·생산량이 같아도 정상품 환산량이 줄면 정상품 톤당 제조원가가 높아질 수 있습니다.','앞 탭의 생산량·원가 가정을 공유하고 기준 수율과 개선 수율을 추가로 입력합니다.','생산량과 수율의 개선 효과를 동시에 또는 개별적으로 비교할 수 있습니다.')
 a,b=st.columns(2)
 with a: y0=st.slider('기준 수율(가정, %)',1.0,100.0,80.0,0.5)
 with b: y1=st.slider('시나리오 수율(가정, %)',1.0,100.0,90.0,0.5)
 scenarios=[('기준',q0,y0),('생산량만 변경',q1,y0),('수율만 변경',q0,y1),('생산량·수율 변경',q1,y1)]
 results=pd.DataFrame([{'시나리오':name,'생산량(톤)':q,'가정 수율(%)':y,**cost(q,y)} for name,q,y in scenarios])
 st.dataframe(results,hide_index=True,use_container_width=True)
 st.plotly_chart(px.bar(results,x='시나리오',y='톤당 제조원가(만원)',text_auto='.2f'),use_container_width=True)
 r0=results.iloc[0]['톤당 제조원가(만원)'];r1=results.iloc[-1]['톤당 제조원가(만원)']
 st.success(f'기준 대비 생산량·수율 통합 개선 효과: {r1-r0:+,.2f}만원/정상품 환산톤 ({(r1/r0-1)*100:+.1f}%)')
 st.warning('수율은 사업보고서 공시값이 아닙니다. 생산실적이 이미 실제 생산제품 수량일 수 있어 여기에 수율을 곱한 값은 가상 정상품 환산량일 뿐입니다. 공정별 실제 투입량·수율·제품 믹스를 반영하지 않습니다.')

with t4:
 st.subheader('표준원가와 실제원가의 차이 분석')
 explain('원가가 계획과 달라진 원인을 가격·사용량·임률·작업능률·조업도 등으로 분해합니다.','첨부한 기존 원가차이 분석 프로그램의 직접재료·직접노무·변동/고정 제조간접원가 분석식을 유지했습니다.','어느 원가요인이 가장 큰 유리/불리 차이를 만드는지 확인합니다.')
 st.warning('이 탭의 값은 모두 사용자 입력입니다. 단위는 원, 재료수량은 동일한 단위, 작업시간·조업도는 시간 기준으로 통일해 입력하세요. ②~③의 억원·만원 시뮬레이션과 금액을 자동 합산하지 않습니다.')
 items=[]
 a,b,c=st.tabs(['직접재료원가','직접노무원가','제조간접원가'])
 with a:
  basis=st.radio('재료 가격차이 계산 기준',['실제사용량','실제구입량'],horizontal=True)
  x,y=st.columns(2)
  with x:
   aq=num('실제사용량(AQ 사용)','dm_aq');buy=num('실제구입량(AQ 구입)','dm_buy');ap=num('실제가격(AP, 원/단위)','dm_ap')
  with y:
   sq=num('표준허용량(SQ)','dm_sq');sp=num('표준가격(SP, 원/단위)','dm_sp')
  pv=(aq if basis=='실제사용량' else buy)*(ap-sp)
  ev=sp*(aq-sq);tv=aq*ap-sq*sp
  for name,v in [('직접재료 가격차이',pv),('직접재료 능률차이',ev)]:items.append((name,v))
  m,n,o=st.columns(3);m.metric('가격차이',money(pv));n.metric('능률차이',money(ev));o.metric('사용기준 총차이',money(tv))
  if basis=='실제구입량' and buy!=aq:st.warning('구입량 기준 가격차이는 사용기준 총차이와 단순 합산 일치하지 않을 수 있습니다. 미사용 재료의 가격차이를 포함하기 때문입니다.')
 with b:
  x,y=st.columns(2)
  with x:ah=num('실제작업시간(AH)','dl_ah');ar=num('실제임률(AR, 원/시간)','dl_ar')
  with y:sh=num('표준허용시간(SH)','dl_sh');sr=num('표준임률(SR, 원/시간)','dl_sr')
  rate=ah*(ar-sr);eff=sr*(ah-sh)
  items.extend([('직접노무 임률차이',rate),('직접노무 능률차이',eff)])
  x,y=st.columns(2);x.metric('임률차이',money(rate));y.metric('능률차이',money(eff))
 with c:
  st.markdown('#### 변동제조간접원가')
  x,y=st.columns(2)
  with x:vh=num('실제조업도(AH)','voh_ah');va=num('실제 변동제조간접원가(원)','voh_actual')
  with y:vs=num('표준허용조업도(SH)','voh_sh');vr=num('표준 변동제조간접원가 배부율(원/시간)','voh_rate')
  spend=va-vh*vr;veff=vr*(vh-vs)
  items.extend([('변동제조간접원가 소비차이',spend),('변동제조간접원가 능률차이',veff)])
  x,y=st.columns(2);x.metric('소비차이',money(spend));y.metric('능률차이',money(veff))
  st.markdown('#### 고정제조간접원가')
  x,y=st.columns(2)
  with x:fa=num('실제 고정제조간접원가(원)','foh_actual');fb=num('예산 고정제조간접원가(원)','foh_budget')
  with y:fd=num('기준조업도(시간)','foh_den');fs=num('표준허용조업도(시간)','foh_sh')
  fr=fb/fd if fd else 0
  bv=fa-fb;vol=fb-fs*fr
  items.extend([('고정제조간접원가 예산차이',bv),('고정제조간접원가 조업도차이',vol)])
  x,y=st.columns(2);x.metric('예산차이',money(bv));y.metric('조업도차이',money(vol))
  if not fd:st.warning('기준조업도가 0이므로 고정제조간접원가 표준배부율과 조업도차이를 정상 계산할 수 없습니다.')
 st.markdown('#### 원가차이 종합결과')
 vd=pd.DataFrame(items,columns=['차이항목','차이금액(원)'])
 vd['판정']=vd['차이금액(원)'].map(sign)
 st.dataframe(vd,hide_index=True,use_container_width=True)
 st.plotly_chart(px.bar(vd,x='차이항목',y='차이금액(원)',color='판정'),use_container_width=True)
 if vd['차이금액(원)'].abs().max()>0:
  lead=vd.loc[vd['차이금액(원)'].abs().idxmax()]
  st.info(f"절댓값 기준 최대 차이: {lead['차이항목']} / {money(lead['차이금액(원)'])}")
 st.caption('재료 가격차이를 실제구입량 기준으로 선택한 경우와 입력 조업도 불일치 시, 모든 차이를 하나의 사용기준 총원가차이로 해석하면 안 됩니다.')

with t5:
 st.subheader('Management Accounting 종합 진단')
 st.markdown('**① 공시에서 확인된 사실**')
 st.write(f"{period} {plant}: 생산능력 {cap:,.0f}톤, 생산실적 {q0:,.0f}톤, 가동률 {base['공시 가동률(%)']:.2f}%")
 st.markdown('**② 사용자 가정에 따른 생산성·단위당 원가**')
 st.write(f'생산량 {q0:,.0f} → {q1:,.0f}톤, 가정 수율 {y0:.1f} → {y1:.1f}%, 정상품 환산 톤당 원가 {r0:,.2f} → {r1:,.2f}만원')
 st.markdown('**③ 원가차이 원인**')
 if vd['차이금액(원)'].abs().max()>0:
  lead=vd.loc[vd['차이금액(원)'].abs().idxmax()]
  st.write(f"가장 큰 차이항목: {lead['차이항목']} ({money(lead['차이금액(원)'])})")
 else:st.write('원가차이 입력값이 모두 0이거나 차이가 없습니다. ④ 탭에 계획·실제 값을 입력하세요.')
 st.markdown('**④ 경영관리 시사점**')
 st.write('생산량 감소로 인한 고정비 배부 부담과 수율 악화로 인한 정상품 환산량 감소를 구분하고, 이후 재료 가격·사용량·임률·능률·제조간접원가 차이를 확인하는 순서가 합리적입니다.')
 st.warning('실제 대한유화의 원가절감 성과나 제품별 제조원가를 계산한 것은 아닙니다. 다품종 연산생산 구조, 공장 간 내부원료 이동, 제품별 원가배부, 정기보수·재고 효과 등은 별도 데이터가 필요합니다.')
 st.markdown('**출처**: 대한유화 2023 사업보고서(2024.03.07), 2024 사업보고서(2025.03.06), 2025 사업보고서(2026.03.05), 2026 반기보고서(2026.08.14), 각 II.3. 원재료 및 생산설비. 사용자 제공 SK바이오사이언스 생산성 시뮬레이터 및 원가차이 분석 코드의 분석 로직을 통합·변경했습니다.')
