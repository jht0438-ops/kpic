import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="대한유화 원가·제품가격·손익 분석",page_icon="📊",layout="wide")
st.title("대한유화 원가·제품가격·손익 분석")
st.caption("2021~2025년 | 한국화학산업협회(KCIA) 연평균 시장가격 + 대한유화 사업보고서 연결손익계산서")

# 시장가격: 사용자가 제공한 KCIA 주요 원자재 가격 동향 화면을 그대로 전사 (US$/톤)
market=pd.DataFrame({
 "연도":[2021,2022,2023,2024,2025],
 "나프타":[647.94,785.71,646.31,673.52,594.84],
 "에틸렌":[1046.67,1007.62,841.82,878.25,813.50],
 "프로필렌":[1041.75,995.00,858.78,851.36,794.18],
 "HDPE":[1062.63,1009.44,891.33,898.43,839.15],
 "PP":[1139.40,1036.31,879.26,893.85,845.33],
})
# 연결 포괄손익계산서 원 단위. 2023/24/25 보고서에서 수치 교차 확인.
fin=pd.DataFrame({
 "연도":[2021,2022,2023,2024,2025],
 "매출액":[2514851601517,2222070977921,2499972627941,2800102662159,3347821791902],
 "매출원가":[2287721342841,2393821096056,2511571765377,2809038413733,3227283794765],
 "판관비":[47716219330,42890227515,50722190280,50956873468,67869094657],
 "영업이익":[179414039346,-214640345650,-62321327716,-59892625042,52668902480]
})
for c in ["매출액","매출원가","판관비","영업이익"]:
 fin[c]=fin[c]/1e8 # 억원
fin["매출총이익"]=fin["매출액"]-fin["매출원가"]
fin["매출원가율"]=fin["매출원가"]/fin["매출액"]*100
fin["영업이익률"]=fin["영업이익"]/fin["매출액"]*100
data=market.merge(fin,on="연도")
for product in ["에틸렌","프로필렌","HDPE","PP"]:
 data[f"{product} 가격차"]=data[product]-data["나프타"]

def conclusion(s):
 st.markdown("#### 이 탭을 통해 얻을 수 있는 결론은 무엇인가요?")
 st.info(s)
def fmt(v, unit=""):
 return f"{v:,.1f}{unit}"
tabs=st.tabs(["① 개요","② 실제 실적","③ 원재료·제품가격","④ 가격차(스프레드)","⑤ 종합 진단"])
with tabs[0]:
 st.subheader("이 프로그램은 무엇인가요?")
 st.write("대한유화의 **실제 연간 손익**과 **나프타·석유화학 제품의 연평균 시장가격**을 함께 분석해, 원가 부담과 제품가격 경쟁이 수익성에 어떤 환경을 만들었는지 살펴보는 FP&A 보조 프로그램입니다.")
 st.markdown("**분석 흐름**: 실제 영업이익 변화 → 나프타 및 제품가격 변화 → 제품별 단순 가격차 → 손익과의 비교")
 st.markdown("**사용 방법**: ②에서 손익을 확인하고, ③에서 시장가격을 비교한 뒤, ④에서 제품별 가격차를 선택하세요. 마지막 ⑤에서 연도별 수익성 변화를 종합합니다.")
 st.warning("시장가격은 대한유화의 실제 매입·판매 단가가 아닙니다. 가격차는 실제 제품별 공헌이익이나 영업이익이 아닙니다. NCC는 복수 제품을 동시에 생산하며 투입수율·에너지비·재고평가·환율·판매량의 영향을 받습니다.")
 st.markdown("**출처**: 한국화학산업협회(KCIA) '주요 원자재 가격 동향' 사용자 제공 화면(2021~2025), 대한유화 2023·2024·2025 사업보고서 연결 포괄손익계산서. 나프타는 CFR Japan, 에틸렌·프로필렌·HDPE·PP는 CFR NEA(2012년 이후) 기준.")
 st.caption("2025년에는 한주가 연결편입되어 연결 실적의 비교가능성에 변화가 있습니다. 이를 제품가격만으로 설명하지 않습니다.")
with tabs[1]:
 st.subheader("2021~2025년 연결 손익 추이")
 display=fin[["연도","매출액","매출원가","판관비","영업이익","매출원가율","영업이익률"]].copy()
 st.dataframe(display.style.format({"매출액":"{:,.1f}","매출원가":"{:,.1f}","판관비":"{:,.1f}","영업이익":"{:,.1f}","매출원가율":"{:.2f}%","영업이익률":"{:.2f}%"}),hide_index=True,use_container_width=True)
 st.caption("금액 단위: 억 원 | 연결 기준")
 fig=go.Figure()
 fig.add_trace(go.Bar(x=fin["연도"].astype(str),y=fin["영업이익"],name="영업이익(억원)"))
 fig.add_hline(y=0,line_color="gray")
 fig.update_layout(height=360,xaxis_title="연도",yaxis_title="억원")
 st.plotly_chart(fig,use_container_width=True)
 yr=st.selectbox("전년 대비 변동을 분석할 연도",[2022,2023,2024,2025],index=3)
 cur=fin.set_index("연도").loc[yr]; prev=fin.set_index("연도").loc[yr-1]
 bridge={"매출 증가 효과":cur["매출액"]-prev["매출액"],"매출원가 증가 효과":-(cur["매출원가"]-prev["매출원가"]),"판관비 증가 효과":-(cur["판관비"]-prev["판관비"])}
 st.markdown(f"**{yr-1} → {yr}년 영업이익 변동 분해 (억원)**")
 cols=st.columns(3)
 for col,(k,v) in zip(cols,bridge.items()): col.metric(k,fmt(v,"억"))
 diff=cur["영업이익"]-prev["영업이익"]
 st.write(f"전년 대비 영업이익 변화 **{diff:+,.1f}억 원** = 매출 효과 {bridge['매출 증가 효과']:+,.1f} + 원가 효과 {bridge['매출원가 증가 효과']:+,.1f} + 판관비 효과 {bridge['판관비 증가 효과']:+,.1f}")
 drivers=sorted(bridge.items(),key=lambda kv:abs(kv[1]),reverse=True)
 conclusion(f"{yr}년 영업이익의 전년 대비 변화는 {diff:+,.1f}억 원입니다. 손익계산서 항목 중 변동폭이 가장 큰 것은 '{drivers[0][0]}'({drivers[0][1]:+,.1f}억 원)입니다. 이는 회계상 증감 분해이며, 원재료 가격이 해당 변동을 유발했다고 단정할 수 없습니다.")
with tabs[2]:
 st.subheader("실제 시장가격 추이")
 product=st.selectbox("비교할 제품",["에틸렌","프로필렌","HDPE","PP"],key="price_product")
 fig=px.line(data,x="연도",y=["나프타",product],markers=True,labels={"value":"US$/톤","variable":"품목"})
 fig.update_layout(height=410,xaxis=dict(tickmode="array",tickvals=[2021,2022,2023,2024,2025]))
 st.plotly_chart(fig,use_container_width=True)
 st.dataframe(market.set_index("연도").style.format("{:,.2f}"),use_container_width=True)
 p0=data.iloc[-2];p1=data.iloc[-1]
 npchg=(p1["나프타"]/p0["나프타"]-1)*100
 prchg=(p1[product]/p0[product]-1)*100
 conclusion(f"2024→2025년 나프타 시장가격은 {npchg:+.1f}%, {product} 시장가격은 {prchg:+.1f}% 변했습니다. 원재료 가격과 제품가격이 서로 다른 폭으로 움직이므로 나프타 가격 하락만으로 수익성 개선을 판단할 수 없습니다.")
with tabs[3]:
 st.subheader("제품별 단순 가격차 분석")
 st.write("**계산식: 제품 시장가격 − 나프타 시장가격 (US$/톤)**")
 st.caption("투입수율을 반영하지 않은 단순 가격차이며, 실제 제조마진·제품별 손익과 다릅니다.")
 product2=st.selectbox("분석 제품",["에틸렌","프로필렌","HDPE","PP"],key="spread_product")
 key=f"{product2} 가격차"
 fig=px.bar(data,x="연도",y=key,text_auto=".1f",labels={key:"단순 가격차(US$/톤)"})
 fig.update_layout(height=400,xaxis=dict(tickmode="array",tickvals=[2021,2022,2023,2024,2025]))
 st.plotly_chart(fig,use_container_width=True)
 spreads=data[["연도"]+[f"{x} 가격차" for x in ["에틸렌","프로필렌","HDPE","PP"]]]
 st.dataframe(spreads.set_index("연도").style.format("{:,.2f}"),use_container_width=True)
 delta=data.iloc[-1][key]-data.iloc[-2][key]
 conclusion(f"{product2}의 단순 가격차는 2024년 {data.iloc[-2][key]:,.2f}달러/톤에서 2025년 {data.iloc[-1][key]:,.2f}달러/톤으로 {delta:+,.2f}달러/톤 변했습니다. 이는 원료와 제품의 상대가격 변화이며 실제 대한유화의 제품별 영업이익 변화를 의미하지는 않습니다.")
with tabs[4]:
 st.subheader("시장가격과 손익의 종합 진단")
 prod=st.selectbox("시장가격 비교 기준",["에틸렌","프로필렌","HDPE","PP"],key="diagnosis_product")
 key=f"{prod} 가격차"
 fig=go.Figure()
 fig.add_trace(go.Bar(x=data["연도"].astype(str),y=data["영업이익"],name="연결 영업이익(억원)",yaxis="y"))
 fig.add_trace(go.Scatter(x=data["연도"].astype(str),y=data[key],mode="lines+markers",name=f"{prod} 단순 가격차(달러/톤)",yaxis="y2"))
 fig.update_layout(height=420,yaxis=dict(title="영업이익(억원)"),yaxis2=dict(title="단순 가격차(달러/톤)",overlaying="y",side="right"),legend=dict(orientation="h",y=1.13))
 st.plotly_chart(fig,use_container_width=True)
 st.markdown("**연도별 점검표**")
 d=data[["연도","영업이익","영업이익률",key]].copy()
 d["영업이익 증감"]=d["영업이익"].diff()
 d["가격차 증감"]=d[key].diff()
 st.dataframe(d.style.format({"영업이익":"{:,.1f}","영업이익률":"{:.2f}%","영업이익 증감":"{:+,.1f}","가격차 증감":"{:+,.2f}",key:"{:,.2f}"}),hide_index=True,use_container_width=True)
 st.markdown("**분석 결과를 해석할 때 추가로 확인할 사항**")
 st.write("① 제품별 판매량·생산량과 가동률 ② 나프타 매입 시점과 재고회전 ③ 환율·유틸리티·고정비 ④ 재고평가손익 ⑤ 2025년 한주 연결편입 효과")
 conclusion("원재료·제품 시장가격의 차이는 수익성 압력을 설명하는 참고 지표입니다. 연결 영업이익은 실제 생산·판매 구성과 회계상 원가, 종속기업 실적에 의해 결정되므로 두 지표의 동행 또는 역행 여부를 확인하고 추가 원인을 검토해야 합니다.")
 st.warning("이 데이터는 연평균 가격입니다. 월별 매입시차(0~3개월)나 재고효과를 계산할 수 없어 해당 기능은 의도적으로 제외했습니다. 월별 실측 가격과 재고자료가 확보되면 별도 탭으로 추가할 수 있습니다.")
