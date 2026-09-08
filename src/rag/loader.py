# src/rag/loader.py

def load_banking_documents():
    """模拟加载银行政策文档，实际可改为读取 PDF/文本文件"""
    docs = [
        "个人住房贷款提前还款需满足贷款满一年，且提前还款金额不低于5万元。",
        "信用卡逾期超过90天将被列入黑名单，并影响个人征信。",
        "企业贷款年利率为4.35%-6.5%，根据企业信用评级浮动。",
        "住房公积金贷款最高额度为120万元，首套住房首付比例不低于30%。",
        "银行账户日累计转账限额为50万元，大额转账需提前预约。",
        "理财产品收益率一般在2%-5%之间，风险等级不同收益不同。",
        "个人信用报告查询次数过多可能影响贷款审批。",
        "反洗钱法规要求单笔现金交易超过5万元需上报。",
        # 可以添加更多
    ]
    return docs

def chunk_texts(docs, chunk_size=200):
    """简单分块：每个文档作为一个块，也可按句子切分"""
    chunks = []
    for idx, doc in enumerate(docs):
        chunks.append({
            "id": f"doc_{idx}",
            "content": doc,
            "metadata": {"source": "bank_policy", "index": idx}
        })
    return chunks