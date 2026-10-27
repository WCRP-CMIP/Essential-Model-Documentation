
<section id="description">

# Calendar (universal)

## Description
Defines the calendar systems used in climate models for time representation. These follow the CF Conventions calendar definitions. The `alias` field contains alternative names for each calendar type.

[View in HTML](https://wcrp-cmip.github.io/Essential-Model-Documentation/calendar/calendar)

</section>

<section id="calendars">

## Available Calendars

| Calendar | Description | Aliases |
| --- | --- | --- |
| standard | Mixed Gregorian/Julian calendar (default) | gregorian |
| proleptic_gregorian | Gregorian rules extended before 1582-10-15 | - |
| 360_day | 12 months × 30 days = 360 days/year | - |
| 365_day | 365 days/year, no leap years | noleap |
| 366_day | 366 days/year, every year is leap | all_leap |
| julian | Julian calendar with 4-year leap cycle | - |
| none | No calendar (time-invariant data) | - |

</section>

<section id="info">

| Item | Reference |
| --- | --- |
| Type | `wcrp:calendar` |
| JSON-LD | `universal:calendar` |
| Expanded reference link | [https://wcrp-cmip.github.io/Essential-Model-Documentation/calendar](https://wcrp-cmip.github.io/Essential-Model-Documentation/calendar) |
| CF Conventions | [Calendar](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#calendar) |

</section>

<section id="usage">

## Usage

### Getting a File

```python
import cmipld
cmipld.get("universal:calendar/standard")
```

</section>
