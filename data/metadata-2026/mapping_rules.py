import re
import unicodedata

OLD_PROVINCE_TO_34 = {'ha giang': 'Tuyên Quang', 'tuyen quang': 'Tuyên Quang', 'cao bang': 'Cao Bằng', 'lai chau': 'Lai Châu', 'lao cai': 'Lào Cai', 'yen bai': 'Lào Cai', 'bac kan': 'Thái Nguyên', 'thai nguyen': 'Thái Nguyên', 'dien bien': 'Điện Biên', 'lang son': 'Lạng Sơn', 'son la': 'Sơn La', 'hoa binh': 'Phú Thọ', 'vinh phuc': 'Phú Thọ', 'phu tho': 'Phú Thọ', 'bac giang': 'Bắc Ninh', 'bac ninh': 'Bắc Ninh', 'quang ninh': 'Quảng Ninh', 'ha noi': 'TP. Hà Nội', 'hanoi': 'TP. Hà Nội', 'hai duong': 'TP. Hải Phòng', 'hai phong': 'TP. Hải Phòng', 'haiphong': 'TP. Hải Phòng', 'thai binh': 'Hưng Yên', 'hung yen': 'Hưng Yên', 'ha nam': 'Ninh Bình', 'ninh binh': 'Ninh Bình', 'nam dinh': 'Ninh Bình', 'thanh hoa': 'Thanh Hóa', 'nghe an': 'Nghệ An', 'ha tinh': 'Hà Tĩnh', 'quang binh': 'Quảng Trị', 'quang tri': 'Quảng Trị', 'thua thien hue': 'TP. Huế', 'hue': 'TP. Huế', 'da nang': 'TP. Đà Nẵng', 'quang nam': 'TP. Đà Nẵng', 'quang ngai': 'Quảng Ngãi', 'kon tum': 'Quảng Ngãi', 'gia lai': 'Gia Lai', 'binh dinh': 'Gia Lai', 'phu yen': 'Đắk Lắk', 'dak lak': 'Đắk Lắk', 'dak nong': 'Lâm Đồng', 'lam dong': 'Lâm Đồng', 'binh thuan': 'Lâm Đồng', 'khanh hoa': 'Khánh Hòa', 'ninh thuan': 'Khánh Hòa', 'binh phuoc': 'Đồng Nai', 'dong nai': 'Đồng Nai', 'tay ninh': 'Tây Ninh', 'long an': 'Tây Ninh', 'binh duong': 'TP. Hồ Chí Minh', 'ho chi minh': 'TP. Hồ Chí Minh', 'ho chi minh city': 'TP. Hồ Chí Minh', 'tp ho chi minh': 'TP. Hồ Chí Minh', 'tphcm': 'TP. Hồ Chí Minh', 'ba ria vung tau': 'TP. Hồ Chí Minh', 'ba ria - vung tau': 'TP. Hồ Chí Minh', 'tien giang': 'Đồng Tháp', 'dong thap': 'Đồng Tháp', 'kien giang': 'An Giang', 'an giang': 'An Giang', 'ben tre': 'Vĩnh Long', 'vinh long': 'Vĩnh Long', 'tra vinh': 'Vĩnh Long', 'soc trang': 'TP. Cần Thơ', 'hau giang': 'TP. Cần Thơ', 'can tho': 'TP. Cần Thơ', 'bac lieu': 'Cà Mau', 'ca mau': 'Cà Mau'}

CITY_TO_34 = {'bien hoa': 'Đồng Nai', 'buon ma thuot': 'Đắk Lắk', 'ca mau': 'Cà Mau', 'can gio': 'TP. Hồ Chí Minh', 'da nang': 'TP. Đà Nẵng', 'dien bien phu': 'Điện Biên', 'di linh': 'Lâm Đồng', 'dong da': 'TP. Hà Nội', 'dong ha': 'Quảng Trị', 'duong to': 'An Giang', 'ha long': 'Quảng Ninh', 'ha tinh': 'Hà Tĩnh', 'hai duong': 'TP. Hải Phòng', 'haiphong': 'TP. Hải Phòng', 'hanoi': 'TP. Hà Nội', 'hoi an': 'TP. Đà Nẵng', 'ho chi minh city': 'TP. Hồ Chí Minh', 'hue': 'TP. Huế', 'kon tum': 'Quảng Ngãi', 'long xuyen': 'An Giang', 'muong nhe': 'Điện Biên', 'nam dinh': 'Ninh Bình', 'nha trang': 'Khánh Hòa', 'phan rang thap cham': 'Khánh Hòa', 'phu quoc': 'An Giang', 'phu rieng': 'Đồng Nai', 'pleiku': 'Gia Lai', 'qui nhon': 'Gia Lai', 'tan an': 'Tây Ninh', 'tan binh': 'TP. Hồ Chí Minh', 'tan phu': 'TP. Hồ Chí Minh', 'thanh hoa': 'Thanh Hóa', 'thu dau mot': 'TP. Hồ Chí Minh', 'vinh': 'Nghệ An', 'vinh long': 'Vĩnh Long', 'vinh yen': 'Phú Thọ'}

ASN_TO_ORGANIZATION = {'7552': 'Viettel', '24086': 'Viettel', '38731': 'Viettel', '133606': 'Viettel', '45899': 'VNPT', '7643': 'VNPT', '135905': 'VNPT', '18403': 'FPT Telecom', '45894': 'FPT Telecom', '140766': 'FPT Telecom', '45903': 'CMC Telecom', '38732': 'CMC Telecom', '38733': 'CMC Telecom', '24088': 'Hanoi Telecom', '38253': 'Hanoi Telecom', '131386': 'Long Van', '131414': 'Long Van', '131423': 'Long Van', '131429': 'MobiFone', '38247': 'Vietnamobile', '7602': 'Saigon Postel', '45543': 'Saigontourist Cable Television', '45544': 'SUPERDATA', '38244': 'VNG', '24173': 'NetNam'}

AS_NAME_ALIASES = {'viettel corporation': 'Viettel', 'viettel group': 'Viettel', 'viettel timor leste': 'Viettel', 'vietel cht compamy ltd': 'Viettel', 'vnpt corp': 'VNPT', 'vietnam posts and telecommunications': 'VNPT', 'vietnam posts and telecommunications group': 'VNPT', 'vietnam posts and telecommunications vnpt': 'VNPT', 'fpt telecom company': 'FPT Telecom', 'fpt online jsc': 'FPT Telecom', 'fpt smart cloud company limited': 'FPT Telecom', 'cmc telecom infrastructure company': 'CMC Telecom', 'hanoi telecom joint stock company hcmc branch': 'Hanoi Telecom', 'hanoi telecom jsc': 'Hanoi Telecom', 'long van system solution jsc': 'Long Van', 'long van soft solution jsc': 'Long Van', 'branch of long van system solution jsc hanoi': 'Long Van', 'mobifone corporation': 'MobiFone', 'vietnamobile telecommunications joint stock company': 'Vietnamobile', 'sai gon postel corporation': 'Saigon Postel', 'vng corporation': 'VNG', 'netnam company': 'NetNam'}

def clean(value: str | None, empty: str = "(empty)") -> str:
    value = (value or "").strip()
    return value if value else empty

def normalize_key(value: str | None) -> str:
    value = clean(value, "")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.replace("Đ", "D").replace("đ", "d")
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return re.sub(r"\s+", " ", value)

def normalized_province_34(row: dict[str, str]) -> str:
    region_key = normalize_key(row.get("region_name"))
    if region_key in OLD_PROVINCE_TO_34:
        return OLD_PROVINCE_TO_34[region_key]

    city_key = normalize_key(row.get("city_name"))
    if city_key in CITY_TO_34:
        return CITY_TO_34[city_key]
    if city_key in OLD_PROVINCE_TO_34:
        return OLD_PROVINCE_TO_34[city_key]

    return "(unmapped)"

def normalized_as_organization(row: dict[str, str]) -> str:
    asn = clean(row.get("asn"), "")
    if asn in ASN_TO_ORGANIZATION:
        return ASN_TO_ORGANIZATION[asn]

    name_key = normalize_key(row.get("as"))
    if name_key in AS_NAME_ALIASES:
        return AS_NAME_ALIASES[name_key]

    return clean(row.get("as"))
