#!/usr/bin/env python3

import os
import re
import sys


_PHOTOS_DESC_NAME = "images/images.tsv"

_YEAR = "2025"
_TRIP_NAME = f"kichik_alay_{_YEAR}"

# input (master) source
_REPORT_NAME = f"source_report_{_TRIP_NAME}.md"
# output source
_REPORT_NAME_CH = f"source_report_{_TRIP_NAME}_ch.md"

# Output files:
# Markdown, for github/view
_OUTPUT_REPORT_NAME_MD = f"report_{_TRIP_NAME}.md"
# PDF, for site/upload
_OUTPUT_REPORT_NAME_PDF = f"report_{_TRIP_NAME}_pdf.md"
# PDF, for champ
_OUTPUT_REPORT_NAME_CH = f"report_{_TRIP_NAME}_ch.md"

_PANDOC = len(sys.argv) > 1 and sys.argv[1] == "pandoc"

_DATA = {
    "ACTIVE_DAYS": "21",
    "CATEGORY_WORD": "III",
    "CHAMP_TITLE_RP": "Чемпионате Москвы",
    "CHAMP_PROTO_DATE": "21.02.2026",  # TODO
    "CHAMP_PROTO": "https://fst-otm.net/f9.pdf",  # TODO
    "DATE_START": "26.07.2025",
    "DATE_END": "15.08.2025",
    "DISTANCE_ALL": "140", # TODO
    "DISTANCE_RATED": "138", # TODO
    "LAST_UPDATE": "20.12.2025",
    "MARSH_CIPHER": "11/3-304",  # TODO
    "MARSH_LINK": "https://<todo>",  # TODO
    "MAX_HEIGHT": "4690",
    "MAX_SLEEP": "TODO",
    "MSU_REPORT_LINK": "https://www.geolink-group.com/tourclub/trips/2025mv3/",
    "NK_TRACK": "https://nakarte.me/#m=12/39.84005/72.55165&l=O/N/F/B/Wp&nktl=Xub6GZHa69C4sn0H4WTJBg",
    "PEOPLE_COUNT": "7",
    "TRIP_NAME": _TRIP_NAME,
    "TLIB_CIPHER": "<todo>",  # TODO
    "VERSION": "0.01", 
    "WESTRA_REPORT_LINK": "https://westra.ru/passes/Reports/???",  # TODO
    "YEAR": _YEAR,
}

def _flush_block(day, photo_block, report_text):
    begin = '<a name="photo_{}"></a>'.format(day)
    end = '<a name="photo_end_{}"></a>'.format(day)
    marker = begin + r'.*?' + end
    # print(marker)
    return re.sub(marker, begin + '\n' + photo_block + end, report_text, flags=re.DOTALL)


def _read_file(file_name):
    text = None
    with open(file_name, encoding="utf-8") as f:
        text = f.read()
    return text


def _write_file(file_name, contents):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(contents)
    print(f"Written {file_name}")


def _replace_metadata(file_name: str) -> str:
    text = _read_file(file_name)
    for key, value in _DATA.items():
        sub = "{" + key + "}"
        print(sub)
        text = text.replace(sub, value)
    return text


def _tex_preprocess(text: str):
    assert "~---" not in text
    text = text.replace("\\т", "&nbsp;&ndash;")
    text = text.replace("\\г", "&deg;")
    text = text.replace("~--", "&nbsp;&ndash;")
    text = text.replace("~", "&nbsp;")
    text = text.replace("<<", "&laquo;")
    text = text.replace(">>", "&raquo;")
    return text


_TEST_TEXT = (
    """GPS), примеченном в походе 2019 года. От Ворошиловских кошей до места ночевки дошли за 1 час 7 минут ЧХВ.

<a name="photo_1"></a>
<a name="1-1"></a>
![](images/DSCF3954.jpg "Фото 1-1. Начало маршрута у погранзаставы Хурзук")
<p style="text-align: center">1-1. Начало маршрута у погранзаставы Хурзук</p>

<a name="1-2"></a>
![](images/DSCF3984.jpg "Фото 1-2. Характер дороги в д.р. Кубань")
<p style="text-align: center">1-2. Характер дороги в д.р. Кубань</p>

<a name="1-3"></a>
![](images/DSCF3966.jpg "Фото 1-3. Каньон р. Кубань")
<p style="text-align: center">1-3. Каньон р. Кубань</p>

<a name="1-4"></a>
![](images/DSCF3994.jpg "Фото 1-4. Характер дороги в д.р. Кубань")
<p style="text-align: center">1-4. Характер дороги в д.р. Кубань</p>

<a name="1-5"></a>
![](images/DSCF4032.jpg "Фото 1-5. Мост через р. Акбаши и место обеда")
<p style="text-align: center">1-5. Мост через р. Акбаши и место обеда</p>

<a name="1-6"></a>
![](images/DSCF4155-Pano.jpg "Фото 1-6. Место стоянки в д.р. Уллу-Езень")
<p style="text-align: center">1-6. Место стоянки в д.р. Уллу-Езень</p>

<a name="photo_end_1"></a>

### День 2. 20 августа 2021 года
*м.н. – д.р. Уллу-Езень - лед. Хасанкой-Сюрюлген - пер. Кичкинекол В. (Сварщиков) (1А) – д. притока р. Кичкинекол*""")


def _load_photos():
    return {}, {}  # disabled

    photos = {}
    photos_by_day = {}

    with open(_PHOTOS_DESC_NAME, encoding='utf-8') as f:
        first = True
        prev_day = None

        day = None
        proper_in_day = 1

        for line in f:
            if first:
                print('SKIPPED:', line)
                first = False
                continue

            line = line.strip()
            cols = [col.strip() for col in line.split('\t')]
            if len(cols) < 5:
                print('BAD', cols)

            photo_id = cols[0]
            day, in_day_id = photo_id.split('-')

            image_name = cols[1].replace(' ', '')
            # author = cols[2]
            # todo = cols[3]
            description = cols[4]
            if description[-1] == '.':
                # cut dots
                description = description[:-1]

            if prev_day != day:
                # skip new line at next day
                prev_day = day
                proper_in_day = 1
                print()

            assert proper_in_day is not None and proper_in_day > 0 and proper_in_day < 30

            print('{:3}   {:3}   {:30}   {}'.format(day, proper_in_day, image_name, description))

            photo = {
                "day": day,
                "in_day": proper_in_day,
                "image_name": image_name,
                "description": description,
            }
            photos[image_name] = photo

            if day not in photos_by_day:
                photos_by_day[day] = []
            photos_by_day[day].append(photo)

            proper_in_day += 1

    assert len(photos) == sum([len(photos_by_day[k]) for k in photos_by_day])

    print("Photos loaded:", len(photos))
    return photos, photos_by_day


def _replace_photo_blocks(photos_by_day, report_text):
    # first, replace photo marks by days
    for day in photos_by_day:
        day_photos = photos_by_day[day]
        photo_block = ""
        for photo in day_photos:
            image_name = photo["image_name"]
            photo_id = "{}-{}".format(day, photo["in_day"])
            # FIXME(2 links)
            photo_link = "images/reduced/{image_name}.jpg".format(image_name=image_name)
            assert os.path.exists(photo_link), photo_link + " does not exist"

            if _PANDOC:
                md_line = (
                    '\n'
                    '![]({photo_link} "Фото {photo_id}. {description}"){{ width=17cm }}\n'
                    '\n'
                    '**Фото {photo_id}**. {description}'
                    '\n'
                ).format(
                    photo_id=photo_id,
                    photo_link=photo_link,
                    description=photo["description"],
                )
            else:
                md_line = (
                    '<div><a name="ph_{photo_id}"></a>\n'
                    '<img src="images/sample_1600/{image_name}.jpg" alt="Фото {photo_id}. {description}" />\n'
                    '<p style="text-align: center; padding-bottom: 12pt; padding-top: 0pt;">'
                    'Фото {photo_id}. {description}</p></div>\n\n'
                ).format(
                    photo_id=photo_id,
                    image_name=image_name,
                    description=photo["description"],
                )

            # print(md_line)
            photo_block += md_line

        print("Replacing block in day", day)
        # print(photo_block)
        new_report_text = _flush_block(day, photo_block, report_text)

        # either replacement is done or text is already weill-formed
        assert new_report_text != report_text or photo_block in report_text
        report_text = new_report_text

    return report_text


def _replace_photo_links(photos, report_text):
    for image_name in photos:
        photo = photos[image_name]
        day = photo["day"]
        photo_id = "{}-{}".format(day, photo["in_day"])
        print("Replacing ", image_name)
        new_report_text = report_text.replace(
            "PHOTO:{}".format(image_name),
            "[Фото {photo_id}](#ph_{photo_id})".format(photo_id=photo_id),
        )
        assert new_report_text != report_text
        report_text = new_report_text

    return report_text


def _post_processing(photos, source_report_text, report_name, output_report_name, write_source=True):

    if write_source:

        # write fixed source
        print("Source fixed, writing output to", report_name)
        _write_file(report_name, source_report_text)

    report_text = source_report_text
    report_text = report_text.replace('\r', '')

    # report_text = _replace_photo_blocks(photos_by_day, report_text)
    # report_text = _replace_photo_links(photos, report_text)

    # write output
    with open(output_report_name, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print("Output written to", output_report_name)


def main():
    # run some tests
    replace_result = _flush_block("1", "REPLACEMENT", _TEST_TEXT)
    assert replace_result != _TEST_TEXT

    source_report_text = _replace_metadata(_REPORT_NAME)
    assert source_report_text

    source_readme_text = _replace_metadata("source_readme.md")
    _write_file("README.md", source_readme_text)

    # regex test
    # assert _TEST_TEXT in source_report_text

    photos, photos_by_day = _load_photos()

    source_report_text = source_report_text.replace('\r', '')
    #source_report_text = _replace_photo_blocks(photos_by_day, source_report_text)

    # fix times in tables
    source_lines = source_report_text.split('\n')
    fixed_source_lines = []
    kosher_source_lines = []
    in_segment_table = False


    for line in source_lines:

        kosher_line = line

        if '|' in line:
            new_line = re.sub(r'([0-9]+)ч ([0-9]+)м', r'\1:\2', line)
            if line != new_line:
                print("Fixed times in:", new_line)
                line = new_line
                kosher_line = new_line
            if 'ЧХВ' in line:
                in_segment_table = True

            """
            if in_segment_table:
                if '-|-' in line:
                    line = "-----|-|-|-|-----"

                cols = line.split('|')
                assert len(cols) == 5, str(len(cols))
                cols[2] = cols[2].replace('ЧХВ группы', 'ЧХВ')
                # remove unnecessary info for champ
                kosher_line = '|'.join(cols[0:3] + [cols[4]])
                print(kosher_line)
            """
        else:
            if in_segment_table:
                in_segment_table = False
                print()

        fixed_source_lines.append(line)
        kosher_source_lines.append(kosher_line)

    source_report_text = '\n'.join(fixed_source_lines)
    ch_report_text = '\n'.join(kosher_source_lines)

    md_report_text = source_report_text.replace('<!--@@BEGIN(MD)-->', '').replace('<!--@@END(MD)-->', '')
    md_report_text = re.sub(r'<!--@@BEGIN.TEX.-->.*<!--@@END.TEX.-->', '', md_report_text, flags=re.DOTALL)
    assert "@@BEGIN" not in md_report_text
    assert "@@END" not in md_report_text

    pdf_report_text = source_report_text.replace('<!--@@BEGIN(TEX)-->', '').replace('<!--@@END(TEX)-->', '')
    pdf_report_text = re.sub(r'<!--@@BEGIN.MD.-->.*<!--@@END.MD.-->', '', pdf_report_text, flags=re.DOTALL)
    assert "@@BEGIN" not in pdf_report_text
    assert "@@END" not in pdf_report_text

    md_report_text = _tex_preprocess(md_report_text)
    pdf_report_text = _tex_preprocess(pdf_report_text)
    ch_report_text = _tex_preprocess(ch_report_text)

    # _post_processing(photos, source_report_text, _REPORT_NAME, _OUTPUT_REPORT_NAME_MD)
    _post_processing(photos, md_report_text, _REPORT_NAME, _OUTPUT_REPORT_NAME_MD, write_source=False)
    _post_processing(photos, pdf_report_text, _REPORT_NAME, _OUTPUT_REPORT_NAME_PDF, write_source=False)
    _post_processing(photos, ch_report_text, _REPORT_NAME_CH, _OUTPUT_REPORT_NAME_CH, write_source=False)


if __name__ == "__main__":
    main()
