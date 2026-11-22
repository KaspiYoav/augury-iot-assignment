*** Settings ***
Library           ../robot_library.py
Test Tags         dfu

*** Variables ***
${UUID}           MOXA_TBCDB1045001

*** Test Cases ***
DFU Is Blocked By Backlog Until It Drains
    [Documentation]    EP with pending backlog must not update; after drain it does.
    ${serial}=    Given An EP With Backlog And New Version Available    EP1    5    2
    When DFU Is Triggered    ${serial}
    Then EP Should Stay At Version    ${serial}    1    deferred_backlog
    When Backlog Is Drained    ${serial}
    And DFU Is Triggered    ${serial}
    Then EP Should Be Updated To Version    ${serial}    2

DFU Is Deferred On Low Battery
    [Documentation]    EP below its battery threshold must not update.
    [Template]    DFU Should Be Deferred For Low Battery
    EP1         2400
    EP2         2499
    CANARY_A    3500

DFU Proceeds At Exactly The Battery Threshold
    [Documentation]    Boundary: battery == threshold is allowed (rule is "below").
    [Template]    DFU Should Succeed At Battery
    EP1         2500
    EP2         2500
    CANARY_A    3600

*** Keywords ***
An EP With Backlog And New Version Available
    [Arguments]    ${ep_type}    ${backlog}    ${new_version}
    Init Node    ${UUID}    33
    ${serial}=    Get EP Serial    ${UUID}    ${ep_type}
    Set EP Backlog    ${serial}    ${backlog}
    Offer EP Version    ${serial}    ${new_version}
    RETURN    ${serial}

DFU Is Triggered
    [Arguments]    ${serial}
    Trigger DFU    ${serial}

Backlog Is Drained
    [Arguments]    ${serial}
    Drain EP Backlog    ${serial}

EP Should Stay At Version
    [Arguments]    ${serial}    ${version}    ${expected_status}
    EP Version Should Be    ${serial}    ${version}
    DFU Status Should Be    ${serial}    ${expected_status}

EP Should Be Updated To Version
    [Arguments]    ${serial}    ${version}
    EP Version Should Be    ${serial}    ${version}
    DFU Status Should Be    ${serial}    success

DFU Should Be Deferred For Low Battery
    [Arguments]    ${ep_type}    ${battery}
    Init Node    ${UUID}    33
    ${serial}=    Get EP Serial    ${UUID}    ${ep_type}
    Set EP Battery    ${serial}    ${battery}
    Offer EP Version    ${serial}    2
    Trigger DFU    ${serial}
    EP Should Stay At Version    ${serial}    1    deferred_low_battery

DFU Should Succeed At Battery
    [Arguments]    ${ep_type}    ${battery}
    Init Node    ${UUID}    33
    ${serial}=    Get EP Serial    ${UUID}    ${ep_type}
    Set EP Battery    ${serial}    ${battery}
    Offer EP Version    ${serial}    2
    Trigger DFU    ${serial}
    EP Should Be Updated To Version    ${serial}    2