# POKERTH.qml-client ... unfinisihed

set(POKERTH_QML_CLIENT_SRC ../../pokerth.cpp
    ../../session.cpp 
    ../../core/loghelper_client.cpp
    ../../net/net_helper_client.cpp
    ../../core/qttools/qthelper/qthelper.cpp
    ../../core/qttools/qttoolswrapper.cpp
    ../../core/qttoolsinterface.cpp
    cpp/retranslate.cpp
    cpp/settingsxmlhandler.cpp
    cpp/settingsmanager.cpp
    cpp/serverconnectionhandler.cpp
    cpp/lobbyhandler.cpp
    cpp/qmlguiinterface.cpp)

qt_add_resources(POKERTH_QML_CLIENT_SRC qml.qrc)

set(QML_FILES
    pokerth.qml
    components/CustomCheckBox.qml
    components/CustomComboBox.qml
    components/CustomTabBar.qml
    components/CustomToggle.qml
    components/GamePlayerBox.qml
    components/GamePlayerSelfBox.qml
    components/GuiSettings.qml
    components/InternetGameSettings.qml
    components/LocalGameSettings.qml
    components/LogsSettings.qml
    components/NetworkGameSettings.qml
    components/NicknameAvatarSettings.qml
    components/ResetSettings.qml
    components/SideMenu.qml
    components/SoundSettings.qml
    components/CustomButton.qml
    components/StyleSettings.qml
    pages/AboutPage.qml
    pages/GamePage.qml
    pages/InternetGamePage.qml
    pages/LocalGamePage.qml
    pages/LogsPage.qml
    pages/NetworkGameCreatePage.qml
    pages/NetworkGameEnterPage.qml
    pages/PreLoader.qml
    pages/SettingsPage.qml
    pages/StartPage.qml
    config/StaticData.qml
    config/Parameters.qml)

set(TS_FILES
    i18n/pokerth_de_DE.ts
    i18n/pokerth_fr_FR.ts
    i18n/pokerth_en_US.ts
)

qt_add_translations(pokerth_qml-client
    TS_FILES        ${TS_FILES}
    SOURCES         ${POKERTH_QML_CLIENT_SRC} ${QML_FILES}
    RESOURCE_PREFIX "/i18n"
)

# Android requires MANUAL_FINALIZATION; all other platforms use standard qt_add_executable
# which triggers qt_finalize_target (adds embind, WASM link options, etc.)
if(ANDROID)
    qt_add_executable(pokerth_qml-client MANUAL_FINALIZATION ${POKERTH_QML_CLIENT_SRC})
    target_include_directories(pokerth_qml-client PRIVATE "${Protobuf_INCLUDE_DIR}")
    target_link_libraries(pokerth_qml-client PUBLIC "${Protobuf_LIBRARIES}")
else()
    qt_add_executable(pokerth_qml-client ${POKERTH_QML_CLIENT_SRC})
endif()

target_include_directories(pokerth_qml-client PUBLIC
    ../../config
    ../../core
    ../../core
    ../../core/qttools
    ../../core/qttools/qthelper
    ../
    .
    cpp)

# Fix für Android: Abseil-Bibliotheken die von Protobuf benötigt werden
if(ANDROID)
    # Suche nach verfügbaren Abseil-Bibliotheken (optional)
    find_library(ABSL_RAW_HASH_SET absl_raw_hash_set PATHS ${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/lib NO_DEFAULT_PATH)
    find_library(ABSL_HASHTABLEZ_SAMPLER absl_hashtablez_sampler PATHS ${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/lib NO_DEFAULT_PATH)
    find_library(ABSL_LOW_LEVEL_HASH absl_low_level_hash PATHS ${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/lib NO_DEFAULT_PATH)
    
    # Erstelle eine Liste der gefundenen Bibliotheken
    set(ABSL_EXTRA_LIBS)
    if(ABSL_RAW_HASH_SET)
        list(APPEND ABSL_EXTRA_LIBS ${ABSL_RAW_HASH_SET})
        message(STATUS "Found absl_raw_hash_set: ${ABSL_RAW_HASH_SET}")
    endif()
    if(ABSL_HASHTABLEZ_SAMPLER)
        list(APPEND ABSL_EXTRA_LIBS ${ABSL_HASHTABLEZ_SAMPLER})
        message(STATUS "Found absl_hashtablez_sampler: ${ABSL_HASHTABLEZ_SAMPLER}")
    endif()
    if(ABSL_LOW_LEVEL_HASH)
        list(APPEND ABSL_EXTRA_LIBS ${ABSL_LOW_LEVEL_HASH})
        message(STATUS "Found absl_low_level_hash: ${ABSL_LOW_LEVEL_HASH}")
    endif()
    
    # Linke die gefundenen Bibliotheken
    if(ABSL_EXTRA_LIBS)
        target_link_libraries(pokerth_qml-client PRIVATE ${ABSL_EXTRA_LIBS})
    else()
        message(WARNING "No additional Abseil libraries found - linking may fail")
    endif()
endif()

target_link_libraries(pokerth_qml-client PUBLIC pokerth_lib)
if(NOT EMSCRIPTEN)
    target_link_libraries(pokerth_qml-client PUBLIC pokerth_db)
endif()

target_link_libraries(pokerth_qml-client PUBLIC pokerth_protocol)
target_link_libraries(pokerth_qml-client PRIVATE Qt6::Core Qt6::Gui Qt6::Quick Qt6::Qml Qt6::Sql Qt6::Xml Qt6::Svg Qt6::QuickControls2 Qt6::Widgets)

target_compile_definitions(pokerth_qml-client PUBLIC QML_CLIENT)

if(EMSCRIPTEN)
    # Increase initial memory — the code+data segment exceeds the 16 MB default.
    target_link_options(pokerth_qml-client PRIVATE "SHELL:-s INITIAL_MEMORY=64MB")

    # Source maps for Debug builds: embeds C++ source locations into a .wasm.map
    # file so Chrome/Firefox DevTools can show step-through C++ debugging without
    # needing DWARF or a separate extension. Requires the .wasm.map to be served
    # alongside the .wasm from the same base URL.
    target_compile_options(pokerth_qml-client PRIVATE
        $<$<CONFIG:Debug>:-gsource-map -O0>)
    target_link_options(pokerth_qml-client PRIVATE
        $<$<CONFIG:Debug>:SHELL:-gsource-map --source-map-base http://localhost:8000/>)

    # Embed a qt.conf at :/qt/etc/qt.conf so Qt's findConfiguration() finds it
    # before calling getRelocatablePrefix(). In a static WASM build, the QT_STATIC
    # branch of getRelocatablePrefix() calls applicationDirPath(), which requires
    # argv[0] to resolve to a real file — impossible in WASM. Providing Prefix=/
    # via qt.conf makes Qt skip that code path entirely.
    set_source_files_properties(wasm_qt.conf PROPERTIES QT_RESOURCE_ALIAS "qt.conf")
    qt_add_resources(pokerth_qml-client "wasm_qt_conf"
        PREFIX "/qt/etc"
        FILES wasm_qt.conf
        BASE "${CMAKE_CURRENT_SOURCE_DIR}"
    )
endif()

# Android: Konfiguriere und finalisiere Target
if(ANDROID)
    # Setze Properties VOR qt_finalize_target
    set_target_properties(pokerth_qml-client PROPERTIES
        QT_ANDROID_PACKAGE_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/android"
        QT_ANDROID_MIN_SDK_VERSION "28"
        QT_ANDROID_TARGET_SDK_VERSION "35"
    )
    
    # Finalisiere das Target (generiert deployment-settings.json)
    qt_finalize_target(pokerth_qml-client)
endif()

install(TARGETS pokerth_qml-client DESTINATION bin OPTIONAL)
install(DIRECTORY ../../../data DESTINATION share/pokerth)
install(FILES ../../../pokerth_qml.desktop DESTINATION share/applications)
install(FILES ../../../pokerth.png DESTINATION share/pixmaps)
