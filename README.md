# Python-SAPCJI3Queuer

Third robot in the SAP CJI3 -> CJI3 pipeline. It does nothing but wait.

## Why it exists

`Python-SAPCJI3Dispatcher` and `Python-SAPCJI3Performer` both drive the SAP GUI, so
both have to run as **blocking** triggers. SAP needs up to ten minutes to generate a
CJI3 spool job, and a blocking robot spent sitting in a poll loop occupies a
scheduler that could be running something useful. Worse, when the dispatcher submits
a whole night's batch and SAP generates those spool jobs one at a time, the performer
can end up waiting per window rather than once.

This robot absorbs that wait. It needs no SAP session and no database - only
OpenOrchestrator - so it can be whitelisted to a scheduler where waiting is cheap.

## Flow

```
Dispatcher (blocking)          Queuer (non-blocking)         Performer (blocking)
  claim windows                                                
  submit CJI3 -> spool                                         
  create element  ---------->  wait until created_date              
  exit immediately             + WAIT_MINUTES                  
                               create element  ------------->  export spool
                                                               merge into MSSQL
```

The wait is a **head start, not a guarantee**. The performer still polls the spool
overview when it takes over (`SPOOL_TIMEOUT_S`, 30 minutes) and still fails if the
job never appears.

## Queues

| | Queue | Element data |
|---|---|---|
| Reads | `SAPCJI3Wait` | `{"UdtraekId": int, "SpoolJob": str}` |
| Writes | `SAPCJI3` | `{"UdtraekId": int, "SpoolJob": str}` |

The timestamp is not in the data - it is the element's own `created_date`, which
OpenOrchestrator stamps when the dispatcher creates it.

## Trigger setup

- **Type:** Queue trigger on `SAPCJI3Wait`, `min_batch_size = 1`.
- **Blocking:** **No.** This is the whole point.
- **Whitelist:** point it at a scheduler that is not running the SAP robots. While
  this robot runs, `poll_triggers` will not start *any* blocking trigger on the same
  scheduler (`OpenOrchestrator/scheduler/runner.py`), so a 15 minute wait here would
  otherwise defer the dispatcher and performer.

A batch does not cost `WAIT_MINUTES` per window. The dispatcher creates one wait
element per window as it works through SAP, so by the time this robot reaches an
element it is already most of the way ripe and only sleeps the gap since the previous
one. Ten windows submitted ~90 seconds apart take about 15 minutes in total, not 150,
and the performer picks up the whole batch when the run finishes.

## Failure handling

A malformed element raises `BusinessError`, which fails that element alone and lets
the run continue. Nothing is lost: the extraction window stays `IGang` in
`dbo.CJI3_Udtraek` until the stale sweep in `usp_CJI3_ReserverUdtraek`
returns it to `Afventer`, and the next dispatcher run submits it again.
