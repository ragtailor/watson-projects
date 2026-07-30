import pytest

from silicon_valley.domain.knowledge_chunk import split_into_chunks


def test_빈_본문은_조각을_만들지_않는다():
    assert split_into_chunks("") == []
    assert split_into_chunks("   \n\t ") == []


def test_chunk_size보다_짧은_본문은_한_조각이다():
    chunks = split_into_chunks("짧은 문서", chunk_size=100, overlap=10)

    assert chunks == ["짧은 문서"]


def test_긴_본문은_여러_조각으로_나뉜다():
    text = "가" * 250

    chunks = split_into_chunks(text, chunk_size=100, overlap=0)

    assert len(chunks) == 3
    assert [len(c) for c in chunks] == [100, 100, 50]
    assert "".join(chunks) == text


def test_겹침만큼_앞_조각의_끝이_다음_조각에_포함된다():
    text = "".join(str(i % 10) for i in range(200))

    chunks = split_into_chunks(text, chunk_size=100, overlap=20)

    assert chunks[0] == text[0:100]
    assert chunks[1] == text[80:180]
    assert chunks[0][-20:] == chunks[1][:20]


def test_모든_조각은_원문_안에_존재한다():
    text = "타이타닉 생존자 분석 보고서. " * 60

    chunks = split_into_chunks(text, chunk_size=120, overlap=30)

    assert chunks
    for chunk in chunks:
        assert chunk in text.strip()


def test_본문_앞뒤_공백은_제거된다():
    chunks = split_into_chunks("  \n실제 본문\n  ", chunk_size=100, overlap=0)

    assert chunks == ["실제 본문"]


@pytest.mark.parametrize(
    "chunk_size, overlap",
    [(0, 0), (-1, 0), (100, -1), (100, 100), (100, 200)],
)
def test_잘못된_인자는_거부한다(chunk_size, overlap):
    with pytest.raises(ValueError):
        split_into_chunks("본문", chunk_size=chunk_size, overlap=overlap)
