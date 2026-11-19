# task-<feature>

State: in progress | pending input | executable | implemented | verified
Complexity tier: S | M | L
Skill version: <first 8 chars of SKILL.md md5> / <YYYY-MM-DD HH:MM>
Blockers: dev <X> / integration <Y> / none <Z>
Source: <PRD file / link / Figma node-id>
Updated: <YYYY-MM-DD> round <N>

## Goal and scope
Goal: <one line>
In scope: <F1, F2…>
Out of scope: <explicitly excluded>
Modules affected: <page / component / API / events / copy>

## Change boundary
| # | Feature point | File / module | Action | What changes here | Blast radius (call sites / shared) | Decision source |

Action is only `change` / `add` / `read-only reference` / `forbidden`.

## F1 <feature name>
State: confirmed | partly pending | implemented | verified
Table applicability: skip <table> (<reason>)

### Logic
- Current state:
- Change:
- Data source and API:
- Mapping to UI:
- Edges and errors:
- Blast radius:

### Function and UI
- Position:
- Trigger:
- Layout:
- Components:
- States:
- Interaction:
- Figma:

### Element list
- <button / option / icon / input / scroll container / dialog / placeholder>: behaviour in one line

### Visual skeleton
| Layer / block | Position | Scrolls / fixed | Container (fill / radius / padding) | Relation to the neighbour layer |

### Visual spec
| Block | Figma node | Text (size / line height / weight / colour) | Size and radius | Padding and gap | Asset logical size |

### Interaction state
| Control | Type | On tap | Before response | After response | Failure / over quota | Re-tap on selected |

### Permission and quota
| Field | Source API | UI when false / used up | Feedback when the user still taps |

### Enum and fallback
| Field | Values | Unknown value handling |

### State → visual
| Backend field | Values | Visual (colour / icon / copy key) | Tappable | Reported |

### UI assets and icons
| Control / area | Reused component | Icon / image | Source | Export | Size and theme fit |

### API failure and degradation
| API | Failure scope | Copy (key) | Retry | Refresh range after retry |

### Partial response and missing fields
| API | Response field set | Missing field handling | May override newer local value |

### Identifiers and external input
| Identifier / input | Source field (sender) | Same key on the receiver | Format constraint | Encoding and sanitation | Missing / invalid |

### Request budget and cache
| Trigger | Requests | Dedupe key | Cache TTL / freshness | Cleanup timing |

### Awaiting an external callback
| Chain | Waits for | Timeout | State restored after timeout | User-visible feedback |

### New abstraction contract
| New abstraction | Consumers (all call sites) | Default params allowed | Same source as the single truth | Out of range / invalid |

### Events

Conclusion: needed or not / reuse or new

**<event_key>** (<short name>)

**Report timing:** <one line>

**Params:**

- **<param>**: <type>. <description>

  - value: <expression> (<file>:<line>)

**Report point**: <file>:<line> or to be added (<feature point / entry>)

-----------

Non-report conditions: <dedupe / second visit / collapsed / logged out>; write `none` when there are none.

### Bilingual
- Conclusion:
- Fields:
- Key plan:

### Acceptance
- <tap this → see that>, every line reproducible by tapping; sentences such as "per the API response" are not acceptance criteria

## Pending items
| # | Feature point | Category | What is missing | Blocking level | Owner | Action after it arrives |

## Question log
| Round | Question keyword | State | Conclusion / landing point |

State is only `answered` / `defaulted` / `asked, awaiting answer` / `void`.

## Risks and dependencies
- <risk / external dependency / party to integrate with>

## Change log
- <YYYY-MM-DD> round <N>: <what this round added or changed>
