*** Settings ***
Library           ../robot_library.py
Test Tags         ota    negative

*** Test Cases ***
Cassia Node Rejects Moxa Artifact
    [Documentation]    Mismatched hardware type: version unchanged, error reported.
    Given A Node At Version    CASSIA_ABC123    33
    When Artifact Is Uploaded    CASSIA_ABC123    moxa_34.swu
    Then Node Should Not Update    CASSIA_ABC123    33
    And Node Should Report Error    CASSIA_ABC123    hardware_mismatch

Matching Artifact Is Accepted Regardless Of Case
    [Documentation]    Hardware type match is case-insensitive.
    Given A Node At Version    MOXA_TBCDB1045001    33
    When Artifact Is Uploaded    MOXA_TBCDB1045001    moxa_34.swu
    Then Node Should Update    MOXA_TBCDB1045001    34

Node With Mixed Case UUID Accepts Lowercase Artifact
    [Documentation]    UUID hardware prefix in a different case still matches.
    Given A Node At Version    Moxa_TBCDB1045002    33
    When Artifact Is Uploaded    Moxa_TBCDB1045002    MOXA_34.swu
    Then Node Should Update    Moxa_TBCDB1045002    34

Malformed Artifact Is Rejected
    [Documentation]    A name that is not <hw>_<version>.swu is a failed OTA.
    Given A Node At Version    MOXA_TBCDB1045001    33
    When Artifact Is Uploaded    MOXA_TBCDB1045001    garbage.txt
    Then Node Should Not Update    MOXA_TBCDB1045001    33
    And Node Should Report Error    MOXA_TBCDB1045001    invalid_artifact

*** Keywords ***
A Node At Version
    [Arguments]    ${uuid}    ${version}
    Init Node    ${uuid}    ${version}
    Node Version Should Be    ${uuid}    ${version}

Artifact Is Uploaded
    [Arguments]    ${uuid}    ${artifact}
    ${status}=    Post Version To Node    ${uuid}    ${artifact}
    Should Be Equal As Integers    ${status}    200

Node Should Not Update
    [Arguments]    ${uuid}    ${version}
    ${reached}=    Wait For Node Version    ${uuid}    99    retries=3    interval=0.1
    Should Not Be True    ${reached}
    Node Version Should Be    ${uuid}    ${version}

Node Should Update
    [Arguments]    ${uuid}    ${version}
    ${reached}=    Wait For Node Version    ${uuid}    ${version}    retries=3    interval=0.1
    Should Be True    ${reached}
    Node Version Should Be    ${uuid}    ${version}

Node Should Report Error
    [Arguments]    ${uuid}    ${text}
    Node Error Should Contain    ${uuid}    ${text}