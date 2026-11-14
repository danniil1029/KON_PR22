# Этап 5. Визуализация графа NuGet

Выполняй команды из папки `demo-stage-5`. Описание всех этапов
и инструкции к итоговой версии находятся в [README проекта](../README.md).

`dot_source` формирует описание на языке Graphviz DOT.
`svg_document` размещает узлы по глубине и рисует стрелки средствами
Python. `save_graph` сохраняет два файла с одним именем и расширениями
`.dot` и `.svg`. Флаг `--tree` выводит ASCII-дерево. Метка `[cycle]`
означает возврат к узлу текущей ветки, `[shown]` — уже показанный узел.

Имена узлов локального графа берутся из JSON. Для NuGet обозначения
`A`, `B`, `C`, …, `Z`, `AA`, … назначаются в порядке BFS.
Обозначения совпадают в DOT, SVG и ASCII-дереве. Полное имя и версия
видны при наведении на узел SVG, в атрибуте `tooltip` файла DOT и
в расшифровке под деревом в консоли.

```powershell
python -m src.main --test --repo tests/fixtures/graph.json --package A --tree --output LOCAL-A.svg
Invoke-Item .\LOCAL-A.svg
```

### Три пакета NuGet

Готовые пары `A.svg`/`A.dot`, `B.svg`/`B.dot`, `C.svg`/`C.dot`
и результаты сравнения находятся в папке [examples](../examples) в корне проекта.
Буквы нумеруются заново в каждом графе, поэтому корень каждой схемы
обозначен `A`.

```powershell
python -m src.main --package Microsoft.Extensions.DependencyInjection --version 8.0.0 --tree --output A.svg
python -m src.main --package Microsoft.Extensions.Options --version 8.0.0 --tree --output B.svg
python -m src.main --package Microsoft.Extensions.Logging --version 8.0.0 --tree --output C.svg
```

| Граф | Корневой пакет NuGet 8.0.0 | Узлы с корнем | Рёбра |
| --- | --- | ---: | ---: |
| `A` | `Microsoft.Extensions.DependencyInjection` | 2 | 1 |
| `B` | `Microsoft.Extensions.Options` | 3 | 2 |
| `C` | `Microsoft.Extensions.Logging` | 6 | 7 |

Ниже приведена расшифровка. Общий префикс имён — `Microsoft.Extensions.`.
Версия всех узлов в этих трёх примерах — `8.0.0`.

| Буква | Граф A | Граф B | Граф C |
| --- | --- | --- | --- |
| A | DependencyInjection | Options | Logging |
| B | DependencyInjection.Abstractions | DependencyInjection.Abstractions | DependencyInjection |
| C | | Primitives | Logging.Abstractions |
| D | | | Options |
| E | | | DependencyInjection.Abstractions |
| F | | | Primitives |

### Сравнение со штатными инструментами .NET

Эталон в `examples/dotnet-comparison.txt` получен на .NET SDK 8.0.408
для `net8.0`. В каждом проверочном проекте использован один корневой
`PackageReference` с точной версией `[8.0.0]`. Имена и версии сверены
по `dotnet list package --include-transitive`, связи — по
`obj/project.assets.json` после `dotnet restore`. Вывод
`dotnet nuget why` показывает пути к общей зависимости.
После введения буквенных обозначений повторно проверены наборы узлов
и рёбер относительно сохранённых результатов. Новые графы получены
через локальный HTTP-репозиторий с тестовыми манифестами по метаданным
NuGet Gallery для `net8.0`. У трёх графов узлы и рёбра совпали.
В дереве программы повторная общая зависимость помечается `[shown]`,
а штатный вывод может повторять её в каждом пути.

Для повторения сравнения создай по одному отдельному проекту
`net8.0` на каждый из трёх корневых пакетов и добавь ссылку на версию
`[8.0.0]`. В папке каждого проекта выполни команды.

```powershell
dotnet restore
dotnet list package --include-transitive
dotnet nuget why Microsoft.Extensions.DependencyInjection.Abstractions
```

Для других пакетов результаты могут различаться. Программа подбирает
минимальную подходящую версию для каждого ребра. При конфликтующих
диапазонах в её графе возможны разные версии одного пакета. NuGet
разрешает версии для проекта целиком и учитывает больше правил выбора
платформ и сред выполнения. Здесь используются обычные диапазоны
версий и выбор точной или совместимой группы для поддерживаемых TFM.
