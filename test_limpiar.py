"""python test_limpiar.py  (o pytest)"""
from main import ROOMS, clean


def test_clean_rellena_y_recorta():
    out = clean({"rules": {"yago": ["a", "b", "c", "d", "e", "f"]}, "done": {}})
    assert out["rules"]["yago"] == ["a", "b", "c", "d", "e"]
    assert out["rules"]["alberto"] == [""] * 5


def test_clean_descarta_basura():
    out = clean({"rules": {"yago": ["x" * 500]}, "done": {"2026-09-21": [ROOMS[0], "jardín"], "mal": "nope"}})
    assert len(out["rules"]["yago"][0]) == 200
    assert out["done"] == {"2026-09-21": [ROOMS[0]]}
    assert clean({}) == clean(clean({}))


def test_general_se_compacta():
    out = clean({"general": ["  fregar  ", "", "   ", "x" * 500, *["y"] * 40]})
    assert out["general"][:2] == ["fregar", "x" * 200]
    assert len(out["general"]) == 30


def test_faults_valida_persona_norma_y_fecha():
    buena = {"d": "2026-09-27", "w": "yago", "r": "fregar"}
    out = clean({"faults": [
        buena,
        {"d": "2026-09-27", "w": "nadie", "r": "fregar"},   # persona que no existe
        {"d": "2026-09-27", "w": "alberto", "r": ""},       # sin norma
        {"w": "alberto", "r": "fregar"},                    # sin fecha
        "basura",
    ]})
    assert out["faults"] == [buena]
    assert len(clean({"faults": [buena] * 600})["faults"]) == 500


if __name__ == "__main__":
    test_clean_rellena_y_recorta()
    test_clean_descarta_basura()
    test_general_se_compacta()
    test_faults_valida_persona_norma_y_fecha()
    print("ok")
