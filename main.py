'''
File: /main.py
File Created: Wednesday, 21st July 2021 5:02:06 pm
Author: ChengCheng Wan <chengcheng.st@gmail.com>
'''
import json
import streamlit as st
import pandas as pd
import base64


st.set_page_config(layout='wide')

datafile = st.text_input('请输入数据URL')


def render(datafile):
    df = pd.read_csv(datafile)

    sidebar = st.sidebar

    sidebar.title('用户调研')
    sidebar.markdown("加载完成，调研`{}`份,问题`{}`个".format(*df.shape))

    group_questions = ['请问您的性别是？', '请问您的出生年代是？',
                       '您所在的城市属于哪个省（直辖市/自治区/特区）？', '请问您的学历是？']

    multiopts_questions = [
        '请问未来1-3年内，您是否有留学或继续深造计划？（多选）',
        '请问您拥有什么类型的汽车？',
        '请问您购买的车型品牌是？',
        '请问您在选择酒店时，通常预定什么等级的酒店？（最多选择两项）',
        '请问您购买过哪些品类的奢侈品？（多选）',
        '请问您购买奢侈品的主要用途是？（多选）',
        '请问您购买奢侈品时的考虑因素有哪些？（多选）',
        '请问您对以下哪些品牌的腕表感兴趣？（多选）',
        '请问您拥有何种品牌的机械腕表？（如有多块儿腕表，请多选）',
        '请问您用过哪些彩妆及肤护品？或者您购买过哪些送人？（多选）',
        '请问您或您的家庭在未来1年内计划购买以下哪些电子产品？（多选）',
        '请问您在购买手机时，主要考虑因素有哪些？（多选）',
        '请问您的子女处在哪个人生阶段？(如您有2个及以上孩子请多选)',
        '请问过去一年您消费占比最高的三项是？',
        '在闲暇时，您主要的消遣方式有哪些？（多选）',
        '请问您经常使用的网购平台是？（多选）',
    ]

    answers = list(
        filter(lambda q: q not in group_questions, list(df.columns)))

    sidebar.subheader("请选择问题")

    ratioqs = sidebar.multiselect(
        "问题", answers, ['请问您是否有海外留学经历？（以学习为目的，在国外停留超过1个月）'])
    sidebar.markdown("""> _已经去除部分问题，如年龄、省份、学历等直接看「群体数据」统计_""")

    sidebar.subheader("数据处理选项")

    sidebar.markdown(
        """> _合并单选、多选为多选，部分问题根据前置选项设计了(单选、多选)两个镜像问题，勾选合并后统一视为为多选，否则按两个问题处理_""")
    merge_questions = sidebar.checkbox("合并同类问题", True)

    sidebar.markdown("""> _多选分裂为多个实体，勾选后可以计算每个选项出现的次数，否则按组合处理_""")
    split_options = sidebar.checkbox("分裂多选问题选项", True)

    def parse_options(cellstr):
        # print('split:', cellstr)
        if cellstr.startswith('['):
            return json.loads(cellstr)
        else:
            return json.loads('["{}"]'.format(cellstr))

    if split_options:
        for column in multiopts_questions:
            # print('merging {}'.format(column))
            if (isinstance(df[column][0], str)):
                df[column] = df[column].fillna("[]").apply(parse_options)
        print()

    sidebar.subheader("分群统计")

    gender_group = sidebar.checkbox("按性别", True)
    age_group = sidebar.checkbox("按年龄", False)
    province_group = sidebar.checkbox("按省份", False)
    education_group = sidebar.checkbox("按学历", False)

    st.subheader("原始数据")
    with st.beta_expander("对应问题的调研数据"):
        for ratioq in ratioqs:
            data = df.loc[:, [ratioq]].reset_index()
            data.columns = ['survey', 'answers']

            st.text(ratioq)
            st.dataframe(data)

    def get_table_download_link(df):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        csv = df.to_csv(index=True)
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}">Download CSV file</a>'
        return href

    def print_statistics(data, title):
        # print('show statistics of', title)
        series = pd.Series([item for sublist in data[title]
                            for item in sublist]) if title in multiopts_questions else data
        c = series.value_counts()
        p = series.value_counts(normalize=True, ascending=False) * 100
        dataframe = pd.concat([c, p], axis=1, keys=[title, '%'])
        st.table(dataframe)
        st.markdown(get_table_download_link(dataframe), unsafe_allow_html=True)

    def render_basic_groups():
        st.subheader("群体数据")
        with st.beta_expander("性别、年龄、学历、省份的基础统计"):

            st.markdown('**性别**')
            print_statistics(df.loc[:, ['请问您的性别是？']], '请问您的性别是？')
            st.markdown('**年龄**')
            print_statistics(df.loc[:, ['请问您的出生年代是？']], '请问您的出生年代是？')
            st.markdown('**学历**')
            print_statistics(df.loc[:, ['请问您的学历是？']], '请问您的学历是？')
            st.markdown('**省份**')
            print_statistics(df.loc[:, ['您所在的城市属于哪个省（直辖市/自治区/特区）？']],
                             '您所在的城市属于哪个省（直辖市/自治区/特区）？')

    render_basic_groups()

    st.title("问题")
    st.markdown("请选择好问题以及分群选项，问题逐个展示")

    groups = list(map(lambda v: v[1], filter(lambda o: o[0], zip(
        [gender_group, age_group, province_group, education_group], group_questions))))

    for ratioq in ratioqs:
        st.subheader(ratioq)
        # filter data
        data = df.loc[:, [ratioq, *groups]]
        print_statistics(data, ratioq)

    st.title("其他问题")
    st.markdown("需要单独计算统计分析的问题，或需要参考多个问卷问题的问题,（单独列出）")
    st.markdown("### 示例：")


if datafile:
    render(datafile)
