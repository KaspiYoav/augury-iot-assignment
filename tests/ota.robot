*** Settings ***
Library           ../robot_library.py
Test Tags         ota

*** Variables ***
${UUID}           MOXA_TBCDB1045001

*** Test Cases ***
OTA Happy Flow
    [Documentation]    Node at v33 receives a matching v34 artifact and updates.
    Given A Node At Version    ${UUID}    33
    When Matching Version Is Uploaded    ${UUID}    moxa_34.swu
    Then Node Should Reach Version    ${UUID}    34

*** Keywords ***
A Node At Version
    [Arguments]    ${uuid}    ${version}
    Init Node    ${uuid}    ${version}
    Node Version Should Be    ${uuid}    ${version}

Matching Version Is Uploaded
    [Arguments]    ${uuid}    ${artifact}
    ${status}=    Post Version To Node    ${uuid}    ${artifact}
    Should Be Equal As Integers    ${status}    200

Node Should Reach Version
    [Arguments]    ${uuid}    ${version}
    ${reached}=    Wait For Node Version    ${uuid}    ${version}    retries=3    interval=0.2
    Should Be True    ${reached}    Node did not reach version ${version}
    Node Version Should Be    ${uuid}    ${version}