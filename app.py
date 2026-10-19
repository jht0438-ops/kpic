import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="대한유화 FP&A 분석", page_icon="📊", layout="wide")
st.markdown("""<style>.block-container{max-width:1250px;padding-top:2rem}
[data-testid="stMetric"]{border:1px solid #e1e5ed;padding:14px;border-radius:12px;background:#f7f9fc}
.small{color:#65748b;font-size:13px}</style>""",unsafe_allow_html=True)
st.title("대한유화 | 원재료 가격·손익 분석")
st.caption("공시 실적 분석 + 가정 기반 민감도 시뮬레이션 · 단위: 억 원 (별도 표기 제외)")
st.warning("공시에서 확인한 실제 실적과 사용자가 설정하는 가상 시나리오를 엄격히 구분합니다. "
           "나프타 실제 구매단가·원료 투입량·제품별 원가는 이 앱에 제공되지 않으며, "
           "시뮬레이션 결과는 대한유화의 실제 손익 전망치가 아닙니다.")

# 연결 손익계산서(2026 반기보고서 p.44): 원 단위 원문 수치
Q2 = dict(sales=956254316742, cogs=941835714651, sga=18295128812, op=-3876526721)
H1 = dict(sales=1803360563654, cogs=1695963696087, sga=37710819835, op=69686047732)
Q1 = {k: H1[k]-Q2[k] for k in H1}
def eok(won): return won / 100_000_000
actual = pd.DataFrame([{"기간":"2026 1분기",**{k:eok(v) for k,v in Q1.items()}},
                       {"기간":"2026 2분기",**{k:eok(v) for k,v in Q2.items()}}],
                      ).set_index("기간")
actual["영업이익률(%)"] = actual["op"]/actual["sales"]*100
names={"sales":"매출액","cogs":"매출원가","sga":"판매비와관리비","op":"영업이익"}
view=actual.rename(columns=names)

t1,t2,t3,t4=st.tabs(["① 실제 실적·변동 분석","② 원재료 가격 시나리오","③ 가동률 확장 분석","④ 분석 방법·출처"])
with t1:
    st.subheader("2026년 1·2분기 실적 비교")
    st.caption("출처: 대한유화 2026.08.14 반기보고서, III. 재무에 관한 사항, 연결 포괄손익계산서 p.44. "
               "1분기 수치는 반기 누적에서 2분기(3개월) 수치를 차감해 계산.")
    a,b,c,d=st.columns(4)
    a.metric("2분기 매출액",f"{actual.loc['2026 2분기','sales']:,.1f}",
             f"{actual.loc['2026 2분기','sales']-actual.loc['2026 1분기','sales']:+,.1f} vs 1분기")
    b.metric("2분기 영업이익",f"{actual.loc['2026 2분기','op']:,.1f}",
             f"{actual.loc['2026 2분기','op']-actual.loc['2026 1분기','op']:+,.1f} vs 1분기")
    c.metric("2분기 매출원가",f"{actual.loc['2026 2분기','cogs']:,.1f}",
             f"{actual.loc['2026 2분기','cogs']-actual.loc['2026 1분기','cogs']:+,.1f} vs 1분기")
    d.metric("2분기 영업이익률",f"{actual.loc['2026 2분기','영업이익률(%)']:.2f}%",
             f"{actual.loc['2026 2분기','영업이익률(%)']-actual.loc['2026 1분기','영업이익률(%)']:+.2f}%p vs 1분기")
    st.dataframe(view.style.format("{:,.2f}"),use_container_width=True)
    fig=go.Figure()
    for col in ["매출액","매출원가","판매비와관리비","영업이익"]:
        fig.add_trace(go.Bar(name=col,x=view.index,y=view[col]))
    fig.update_layout(barmode="group",height=390,yaxis_title="억 원",legend_orientation="h")
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("#### 영업이익 변동 브리지")
    changes={k:actual.iloc[1][k]-actual.iloc[0][k] for k in ["sales","cogs","sga","op"]}
    bridge=pd.DataFrame({"항목":["1분기 영업이익","매출액 증가 효과","매출원가 증가 효과","판관비 증가 효과","2분기 영업이익"],
                         "금액":[actual.iloc[0]["op"],changes["sales"],-changes["cogs"],-changes["sga"],actual.iloc[1]["op"]]})
    fig2=go.Figure(go.Waterfall(x=bridge["항목"],y=bridge["금액"],
                               measure=["absolute","relative","relative","relative","total"],
                               text=[f"{v:+,.1f}" for v in bridge["금액"]],textposition="outside"))
    fig2.update_layout(height=380,yaxis_title="억 원",showlegend=False)
    st.plotly_chart(fig2,use_container_width=True)
    st.info("이 브리지는 회계상 손익 항목의 증감만 분해합니다. 매출원가 증가 중 얼마가 나프타 가격, "
            "재고효과, 판매량, 환율, 연결 자회사 변화에서 발생했는지는 공시만으로 분리할 수 없습니다.")

with t2:
    st.subheader("나프타 가격·원가 반영 시차 시뮬레이션")
    st.write("**기준:** 2026년 2분기 실제 영업이익을 출발점으로 삼아, '원재료 노출 원가'의 가상 변화만 반영합니다.")
    st.caption("가격·원료 비중·시차·판매가격 전가율은 모두 사용자 가정입니다. 실제 공시 원가 구조로 오인하지 마세요.")
    l,r=st.columns(2)
    with l:
        pct=st.slider("매출원가 중 나프타 가격 변동에 노출된 비중 (가정, %)",0,100,45,5)
        change=st.slider("나프타 가격 변화율 (가정, %)",-40,40,10,1)
        pass_through=st.slider("가격 변화를 제품 판매가격에 전가하는 비율 (가정, %)",0,100,30,5)
    with r:
        lag=st.slider("이번 분기에 원가로 반영되는 비율 (가정, %)",0,100,50,5)
        volume=st.slider("매출·원가 물량 변화율 (가정, %)",-20,20,0,1)
        st.caption("반영 비율 0%=다음 분기로 전액 이연, 100%=이번 분기에 전액 반영. "
                   "시차 효과는 단순화한 모형이며 실제 재고평가손실과 다릅니다.")
    base=actual.loc["2026 2분기"]
    exposed=base["cogs"]*pct/100
    # 가격 변화는 원재료 노출 원가에, 판매가격 전가는 동일한 금액 기반으로 적용한 단순 가정
    cost_price_effect=exposed*(change/100)*(lag/100)
    revenue_price_effect=exposed*(change/100)*(pass_through/100)
    revenue_volume_effect=base["sales"]*(volume/100)
    cost_volume_effect=base["cogs"]*(volume/100)
    op_new=base["op"]+revenue_price_effect-cost_price_effect+revenue_volume_effect-cost_volume_effect
    x,y,z=st.columns(3)
    x.metric("실제 기준 영업이익",f"{base['op']:,.1f}억")
    y.metric("가상 손익 영향",f"{op_new-base['op']:+,.1f}억")
    z.metric("가상 조정 영업이익",f"{op_new:,.1f}억")
    fig=go.Figure(go.Waterfall(
        x=["실제 2분기 영업이익","제품가격 전가 가정","원가 반영 가정","물량 증가 매출","물량 증가 원가","시나리오 영업이익"],
        y=[base["op"],revenue_price_effect,-cost_price_effect,revenue_volume_effect,-cost_volume_effect,op_new],
        measure=["absolute","relative","relative","relative","relative","total"]))
    fig.update_layout(height=410,yaxis_title="억 원")
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("#### 원재료 가격 변동별 민감도")
    vals=np.arange(-30,31,5)
    def simulate(p):
        return base["op"]+exposed*(p/100)*(pass_through/100-lag/100)+revenue_volume_effect-cost_volume_effect
    sen=pd.DataFrame({"나프타 가격 변동(%)":vals,"가상 영업이익(억 원)":[simulate(v) for v in vals]})
    f=go.Figure(go.Scatter(x=sen.iloc[:,0],y=sen.iloc[:,1],mode="lines+markers"))
    f.add_hline(y=0,line_dash="dash")
    f.update_layout(height=350,xaxis_title="나프타 가격 변동률(%)",yaxis_title="가상 영업이익(억 원)")
    st.plotly_chart(f,use_container_width=True)
    st.dataframe(sen.style.format({"가상 영업이익(억 원)":"{:,.1f}"}),use_container_width=True)
    st.download_button("시나리오 표 CSV 다운로드",sen.to_csv(index=False).encode("utf-8-sig"),
                       file_name="KPIC_naphtha_sensitivity.csv",mime="text/csv")

with t3:
    st.subheader("가동률 변화에 따른 제조원가 · 선택적 확장")
    st.warning("공시에서 대한유화 NCC의 실제 고정비·변동비 분리가 확인되지 않아, 이 탭은 **100% 가정 기반 교육용 모델**입니다. "
               "1·2번 탭과 독립적인 모형이며 실제 실적과 직접 연결하지 않습니다.")
    a,b=st.columns(2)
    with a:
        capacity=st.number_input("연간 생산능력 (가상, 톤)",min_value=1000,max_value=5000000,value=900000,step=10000)
        util=st.slider("가동률 (%)",30,100,70,5)
        fixed=st.number_input("연간 고정비 (가상, 억 원)",min_value=0.0,value=2500.0,step=100.0)
    with b:
        variable=st.number_input("톤당 변동원가 (가상, 만 원)",min_value=0.0,value=90.0,step=5.0)
        price=st.number_input("톤당 판매가격 (가상, 만 원)",min_value=0.0,value=125.0,step=5.0)
    tonnes=capacity*util/100
    revenue=tonnes*price/10000
    var_cost=tonnes*variable/10000
    profit=revenue-var_cost-fixed
    a,b,c=st.columns(3)
    a.metric("생산량",f"{tonnes:,.0f}톤")
    b.metric("톤당 총원가",f"{(fixed*10000/tonnes+variable):,.1f}만 원")
    c.metric("가상 영업손익",f"{profit:,.1f}억 원")
    rows=[]
    for u in range(30,101,5):
        q=capacity*u/100
        rows.append({"가동률(%)":u,"톤당 총원가(만 원)":fixed*10000/q+variable,
                     "영업손익(억 원)":q*(price-variable)/10000-fixed})
    frame=pd.DataFrame(rows)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=frame["가동률(%)"],y=frame["영업손익(억 원)"],name="영업손익"))
    fig.add_hline(y=0,line_dash="dash")
    fig.update_layout(height=350,yaxis_title="억 원")
    st.plotly_chart(fig,use_container_width=True)
    if price>variable:
        break_even=fixed*10000/(capacity*(price-variable))*100
        st.write(f"**가정상 손익분기 가동률:** {break_even:,.1f}% "
                 + ("(설정 범위 밖)" if break_even>100 else ""))
    else:
        st.write("판매가격이 톤당 변동원가 이하이므로 가동률을 올려도 고정비를 회수할 수 없습니다.")
    st.caption("실제 NCC는 에틸렌·프로필렌 등 여러 제품이 함께 생산됩니다. "
               "단일 제품 가격·원가 모형은 결합원가 배부와 제품 믹스를 반영하지 않습니다.")

with t4:
    st.subheader("근거와 해석 범위")
    st.markdown("""
**확인된 공시 자료**
- 대한유화 「반기보고서(2026.08.14)」 p.44: 연결 포괄손익계산서(반기 누적 및 2분기 3개월 실적).
- 같은 보고서 p.17~26: 주요 제품·원재료·생산설비에 관한 공시.
- 「사업보고서(2026.03.05)」: 2025년 사업 구조와 한주 연결 편입 참고.
- 「대한유화 심층분석보고서」: 나프타 가격·래깅 효과·가동률과 관련된 분석 주제의 출발점.

**계산 원칙**
1. 1분기 실제 실적 = 2026년 상반기 누적 실적 − 2분기(3개월) 실적.
2. 영업이익 = 매출액 − 매출원가 − 판매비와관리비. 원 단위 계산 후 억 원 표시.
3. 2번 탭은 2분기 실제 영업이익에 *가정상* 원재료 가격 변화, 제품가격 전가, 물량 변화를 가감.
4. 3번 탭은 가상 생산량 × (가상 판매단가 − 가상 변동원가) − 가상 고정비.

**제한 사항**
- 외부 나프타 가격 데이터 및 대한유화의 실제 매입단가는 탑재하지 않았습니다.
- 재고평가손실을 직접 산출하지 않으며, 원가 반영 비율로 시차를 단순 근사합니다.
- 연결 실적에는 석유화학 이외의 사업도 포함됩니다. 나프타 민감도는 연결 전체의 실증적 추정이 아닙니다.
- 2025년 한주 연결 편입으로 과거 연도와 연결 매출·이익 비교 시 주의가 필요합니다.
- 실제 재무 전망이나 투자 판단에 사용하기 전에 내부 원가·판매량·재고 데이터로 보정해야 합니다.
""")
