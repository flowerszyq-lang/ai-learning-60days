@router.get("/search")
async def search(query: str, db: AsyncSession = Depends(get_db)):
    query_embedding = embed_text(query)
    # 使用 pgvector 的余弦相似度查询
    stmt = select(Document).order_by(Document.embedding.cosine_distance(query_embedding)).limit(5)
    result = await db.execute(stmt)
    docs = result.scalars().all()
    return [{"content": d.content, "metadata": d.metadata} for d in docs]