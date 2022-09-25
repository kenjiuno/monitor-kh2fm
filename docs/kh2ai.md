# KH2 ai

Update timestamp: Sun Sep 25 08:17:23 2022 UTC

## Credits

The basic research result is inherited from Govanify's works.

- [Kingdom Hearts II - AI ISA](https://openkh.dev/kh2/file/ai/kh2ai.html)

## Language

Maybe: [Stack machine - Wikipedia](https://en.wikipedia.org/wiki/Stack_machine)

## File format

```c
struct header {
    char name[16];
    s32 workSize;
    s32 stackSize;
    s32 termSize;
    struct {
        s32 trigger; // key
        s32 entry; // pointer to code
    } triggers[n];
    s32 endTrigger; // 0
    s32 endEntry; // 0
};
```

## Memory space

4 kinds:

- work
- stack
- temp
- ai

### work

Uninitialized memory space.

It is like `.bss` [.bss - Wikipedia](https://en.wikipedia.org/wiki/.bss)

```c
char workmem[512];

void main() {

}
```

### stack

The local work area belongs to function block against each call.

- `gosub` can allocate this stack.
- `ret` can release it.

```c
void func() {
    int var1;
}
```

### temp stack

4 bytes per stack operation.

It has limited access from script.

It acts like real stack memory used by assembly language.

For example: using for local mathematical operations (add, sub, etc), and in/out arguments against function call.

The function block has implicit rule to declare how many in/out stack variables counts.

```c
// 2 stack in
// 1 stack out
int func(int a, int b) {
    return a + b;
}

void main() {
    int res = func(123, 456);
}
```

### ai

Referencing static data.

```c
static char text[] = "hello";

void main() {
    puts(text);
}
```

## Instrument format

4 patterns:

- 16 bits only. (used in unary and binary operators and so on)
- 16 bits +16 bits 1 arg. (branch, syscall and so on)
- 16 bits +16 bits 2 args. (memcpyTo*)
- 16 bits +32 bits 1 arg. (pushImm and gosub32)

Basic form:

```
FEDCBA9876 54 3210
---- ssub sub opcode
0000000000 00 0000 +u32: PUSH.V ri
```

Instrument list:

| opcode | sub | ssub | name |
|--:|--:|--:|---|
| 0 | 0 | None | [pushImm](#pushimm) |
| 0 | 1 | None | [pushImm](#pushimm) |
| 0 | 2 | 0 | [pushFromPSp](#pushfrompsp) |
| 0 | 2 | 1 | [pushFromPWp](#pushfrompwp) |
| 0 | 2 | 2 | [pushFromPSpVal](#pushfrompspval) |
| 0 | 2 | 3 | [pushFromPAi](#pushfrompai) |
| 0 | 3 | 0 | [pushFromFSp](#pushfromfsp) |
| 0 | 3 | 1 | [pushFromFWp](#pushfromfwp) |
| 0 | 3 | 2 | [pushFromFSpVal](#pushfromfspval) |
| 0 | 3 | 3 | [pushFromFAi](#pushfromfai) |
| 1 | None | 0 | [popToSp](#poptosp) |
| 1 | None | 1 | [popToWp](#poptowp) |
| 1 | None | 2 | [popToSpVal](#poptospval) |
| 1 | None | 3 | [popToAi](#poptoai) |
| 2 | None | 0 | [memcpyToSp](#memcpytosp) |
| 2 | None | 1 | [memcpyToWp](#memcpytowp) |
| 2 | None | 2 | [memcpyToSpVal](#memcpytospval) |
| 2 | None | 3 | [memcpyToSpAi](#memcpytospai) |
| 3 | None | None | [fetchValue](#fetchvalue) |
| 4 | None | None | [memcpy](#memcpy) |
| 5 | 0 | 0 | [cfti](#cfti) |
| 5 | 0 | 2 | [neg](#neg) |
| 5 | 0 | 3 | [inv](#inv) |
| 5 | 0 | 4 | [eqz](#eqz) |
| 5 | 0 | 5 | [abs](#abs) |
| 5 | 0 | 6 | [msb](#msb) |
| 5 | 0 | 7 | [info](#info) |
| 5 | 0 | 8 | [eqz](#eqz) |
| 5 | 0 | 9 | [neqz](#neqz) |
| 5 | 0 | 10 | [msbi](#msbi) |
| 5 | 0 | 11 | [ipos](#ipos) |
| 5 | 1 | 1 | [citf](#citf) |
| 5 | 1 | 2 | [negf](#negf) |
| 5 | 1 | 5 | [absf](#absf) |
| 5 | 1 | 6 | [infzf](#infzf) |
| 5 | 1 | 7 | [infoezf](#infoezf) |
| 5 | 1 | 8 | [eqzf](#eqzf) |
| 5 | 1 | 9 | [neqzf](#neqzf) |
| 5 | 1 | 10 | [supoezf](#supoezf) |
| 5 | 1 | 11 | [supzf](#supzf) |
| 6 | 0 | 0 | [add](#add) |
| 6 | 0 | 1 | [sub](#sub) |
| 6 | 0 | 2 | [mul](#mul) |
| 6 | 0 | 3 | [div](#div) |
| 6 | 0 | 4 | [mod](#mod) |
| 6 | 0 | 5 | [and](#and) |
| 6 | 0 | 6 | [or](#or) |
| 6 | 0 | 7 | [xor](#xor) |
| 6 | 0 | 8 | [sll](#sll) |
| 6 | 0 | 9 | [sra](#sra) |
| 6 | 0 | 10 | [eqzv](#eqzv) |
| 6 | 0 | 11 | [neqzv](#neqzv) |
| 6 | 1 | 0 | [addf](#addf) |
| 6 | 1 | 1 | [subf](#subf) |
| 6 | 1 | 2 | [mulf](#mulf) |
| 6 | 1 | 3 | [divf](#divf) |
| 6 | 1 | 4 | [modf](#modf) |
| 7 | None | 0 | [jmp](#jmp) |
| 7 | None | 1 | [jnz](#jnz) |
| 7 | None | 2 | [jz](#jz) |
| 8 | None | None | [gosub](#gosub) |
| 9 | None | 0 | [halt](#halt) |
| 9 | None | 1 | [exit](#exit) |
| 9 | None | 2 | [ret](#ret) |
| 9 | None | 3 | [drop](#drop) |
| 9 | None | 5 | [dup](#dup) |
| 9 | None | 6 | [sin](#sin) |
| 9 | None | 7 | [cos](#cos) |
| 9 | None | 8 | [degr](#degr) |
| 9 | None | 9 | [radd](#radd) |
| 10 | None | None | [syscall](#syscall) |
| 11 | None | None | [gosub32](#gosub32) |

## Syscall

Notes:

- tableIdx = _ssub_
- funcIdx = _imm16_

Syscall list:

| tableIdx | funcIdx | name |
|--:|--:|---|
| 0 | 0 | [trap_puti](#trap_puti) |
| 0 | 1 | [trap_putf](#trap_putf) |
| 0 | 2 | [trap_puts](#trap_puts) |
| 0 | 3 | [trap_frametime](#trap_frametime) |
| 0 | 4 | [trap_vector_add](#trap_vector_add) |
| 0 | 5 | [trap_vector_sub](#trap_vector_sub) |
| 0 | 6 | [trap_vector_len](#trap_vector_len) |
| 0 | 7 | [trap_vector_normalize](#trap_vector_normalize) |
| 0 | 8 | [trap_vector_dump](#trap_vector_dump) |
| 0 | 9 | [trap_thread_start](#trap_thread_start) |
| 0 | 11 | [trap_file_is_reading](#trap_file_is_reading) |
| 0 | 12 | [trap_file_flush](#trap_file_flush) |
| 0 | 13 | [trap_vector_roty](#trap_vector_roty) |
| 0 | 14 | [trap_progress_set_flag](#trap_progress_set_flag) |
| 0 | 15 | [trap_progress_check_flag](#trap_progress_check_flag) |
| 0 | 16 | [trap_random_get](#trap_random_get) |
| 0 | 17 | [trap_random_getf](#trap_random_getf) |
| 0 | 18 | [trap_random_range](#trap_random_range) |
| 0 | 19 | [trap_worldflag_set](#trap_worldflag_set) |
| 0 | 20 | [trap_worldflag_check](#trap_worldflag_check) |
| 0 | 21 | [trap_vector_get_rot_xz](#trap_vector_get_rot_xz) |
| 0 | 22 | [trap_abs](#trap_abs) |
| 0 | 23 | [trap_absf](#trap_absf) |
| 0 | 24 | [trap_stputi](#trap_stputi) |
| 0 | 25 | [trap_stputf](#trap_stputf) |
| 0 | 26 | [trap_stputs](#trap_stputs) |
| 0 | 27 | [func_system_set_game_speed](#func_system_set_game_speed) |
| 0 | 28 | [method_blur_init](#method_blur_init) |
| 0 | 29 | [method_blur_start](#method_blur_start) |
| 0 | 30 | [method_blur_stop](#method_blur_stop) |
| 0 | 31 | [func_screen_whiteout](#func_screen_whiteout) |
| 0 | 32 | [func_screen_whitein](#func_screen_whitein) |
| 0 | 35 | [method_vector_scale](#method_vector_scale) |
| 0 | 36 | [trap_vector_mul](#trap_vector_mul) |
| 0 | 37 | [trap_vector_div](#trap_vector_div) |
| 0 | 38 | [trap_effect_set_pos](#trap_effect_set_pos) |
| 0 | 39 | [trap_effect_set_scale](#trap_effect_set_scale) |
| 0 | 40 | [trap_effect_set_rot](#trap_effect_set_rot) |
| 0 | 41 | [trap_effect_set_dir](#trap_effect_set_dir) |
| 0 | 42 | [trap_vector_atan_xz](#trap_vector_atan_xz) |
| 0 | 43 | [trap_fixrad](#trap_fixrad) |
| 0 | 44 | [trap_effect_loop_end](#trap_effect_loop_end) |
| 0 | 45 | [trap_vector_addf](#trap_vector_addf) |
| 0 | 46 | [trap_vector_homing](#trap_vector_homing) |
| 0 | 47 | [trap_memory_alloc](#trap_memory_alloc) |
| 0 | 48 | [trap_memory_free](#trap_memory_free) |
| 0 | 49 | [trap_effect_is_alive](#trap_effect_is_alive) |
| 0 | 50 | [trap_effect_is_active](#trap_effect_is_active) |
| 0 | 51 | [trap_effect_kill](#trap_effect_kill) |
| 0 | 52 | [trap_effect_fadeout](#trap_effect_fadeout) |
| 0 | 53 | [trap_effect_pos](#trap_effect_pos) |
| 0 | 54 | [trap_effect_dir](#trap_effect_dir) |
| 0 | 55 | [trap_timer_count_down](#trap_timer_count_down) |
| 0 | 56 | [trap_timer_count_up](#trap_timer_count_up) |
| 0 | 57 | [trap_saveflag_set](#trap_saveflag_set) |
| 0 | 58 | [trap_saveflag_reset](#trap_saveflag_reset) |
| 0 | 59 | [trap_saveflag_check](#trap_saveflag_check) |
| 0 | 60 | [trap_assert](#trap_assert) |
| 0 | 61 | [trap_saveram_get_partram](#trap_saveram_get_partram) |
| 0 | 62 | [trap_partram_set_item_max](#trap_partram_set_item_max) |
| 0 | 63 | [trap_item_get](#trap_item_get) |
| 0 | 64 | [trap_sound_disable](#trap_sound_disable) |
| 0 | 65 | [trap_sound_play_system](#trap_sound_play_system) |
| 0 | 66 | [trap_effect_pause](#trap_effect_pause) |
| 0 | 67 | [trap_effect_set_color](#trap_effect_set_color) |
| 0 | 68 | [trap_vector_rotx](#trap_vector_rotx) |
| 0 | 69 | [trap_menuflag_set](#trap_menuflag_set) |
| 0 | 70 | [trap_progress_is_second](#trap_progress_is_second) |
| 0 | 73 | [trap_menuflag_reset](#trap_menuflag_reset) |
| 0 | 74 | [trap_screen_show_picture](#trap_screen_show_picture) |
| 0 | 75 | [trap_saveram_set_weapon](#trap_saveram_set_weapon) |
| 0 | 76 | [trap_saveram_set_form_weapon](#trap_saveram_set_form_weapon) |
| 0 | 77 | [trap_screen_cross_fade](#trap_screen_cross_fade) |
| 0 | 78 | [trap_vector_inter](#trap_vector_inter) |
| 0 | 79 | [trap_effect_add_dead_block](#trap_effect_add_dead_block) |
| 0 | 80 | [trap_pad_is_button](#trap_pad_is_button) |
| 0 | 81 | [trap_pad_is_trigger](#trap_pad_is_trigger) |
| 0 | 82 | [trap_vector_outer_product](#trap_vector_outer_product) |
| 0 | 83 | [trap_vector_rot](#trap_vector_rot) |
| 0 | 84 | [trap_vector_angle](#trap_vector_angle) |
| 0 | 85 | [trap_effect_loop_end_kill](#trap_effect_loop_end_kill) |
| 0 | 86 | [trap_effect_set_type](#trap_effect_set_type) |
| 0 | 87 | [trap_screen_fadeout](#trap_screen_fadeout) |
| 0 | 88 | [trap_screen_fadein](#trap_screen_fadein) |
| 0 | 89 | [trap_menuflag_check](#trap_menuflag_check) |
| 0 | 90 | [trap_vector_draw](#trap_vector_draw) |
| 0 | 91 | [trap_vector_inner_prodcut](#trap_vector_inner_prodcut) |
| 0 | 92 | [trap_partram_add_attack](#trap_partram_add_attack) |
| 0 | 93 | [trap_partram_add_wisdom](#trap_partram_add_wisdom) |
| 0 | 94 | [trap_partram_add_defence](#trap_partram_add_defence) |
| 0 | 95 | [trap_partram_set_levelup_type](#trap_partram_set_levelup_type) |
| 0 | 96 | [trap_partram_add_ap](#trap_partram_add_ap) |
| 0 | 97 | [trap_item_reduce](#trap_item_reduce) |
| 0 | 98 | [trap_saveram_set_form_ability](#trap_saveram_set_form_ability) |
| 0 | 99 | [trap_partram_add_ability](#trap_partram_add_ability) |
| 0 | 100 | [trap_saveram_increment_friend_recov](#trap_saveram_increment_friend_recov) |
| 0 | 101 | [trap_progress_is_secret_movie](#trap_progress_is_secret_movie) |
| 0 | 102 | [trap_vector_to_angle](#trap_vector_to_angle) |
| 0 | 103 | [trap_progress_is_fm_secret_movie](#trap_progress_is_fm_secret_movie) |
| 0 | 104 | [trap_sound_set_bgse_volume](#trap_sound_set_bgse_volume) |
| 1 | 0 | [trap_sysobj_appear](#trap_sysobj_appear) |
| 1 | 1 | [trap_obj_set_rot](#trap_obj_set_rot) |
| 1 | 2 | [trap_sysobj_moveto](#trap_sysobj_moveto) |
| 1 | 3 | [trap_sysobj_player](#trap_sysobj_player) |
| 1 | 4 | [trap_obj_wish_dir](#trap_obj_wish_dir) |
| 1 | 5 | [trap_act_table_init](#trap_act_table_init) |
| 1 | 6 | [trap_act_table_add](#trap_act_table_add) |
| 1 | 7 | [trap_obj_set_act_table](#trap_obj_set_act_table) |
| 1 | 8 | [trap_obj_act_start](#trap_obj_act_start) |
| 1 | 9 | [trap_obj_act_push](#trap_obj_act_push) |
| 1 | 10 | [trap_obj_is_act_exec](#trap_obj_is_act_exec) |
| 1 | 11 | [trap_sysobj_motion_start](#trap_sysobj_motion_start) |
| 1 | 12 | [trap_sysobj_motion_change](#trap_sysobj_motion_change) |
| 1 | 13 | [trap_sysobj_motion_push](#trap_sysobj_motion_push) |
| 1 | 14 | [trap_sysobj_motion_is_end](#trap_sysobj_motion_is_end) |
| 1 | 15 | [trap_sysobj_motion_id](#trap_sysobj_motion_id) |
| 1 | 17 | [trap_obj_leave_force](#trap_obj_leave_force) |
| 1 | 18 | [trap_obj_attach](#trap_obj_attach) |
| 1 | 19 | [trap_sysobj_fadeout](#trap_sysobj_fadeout) |
| 1 | 20 | [trap_sysobj_fadein](#trap_sysobj_fadein) |
| 1 | 21 | [trap_obj_effect_start](#trap_obj_effect_start) |
| 1 | 22 | [trap_obj_effect_start_pos](#trap_obj_effect_start_pos) |
| 1 | 23 | [trap_area_world](#trap_area_world) |
| 1 | 24 | [trap_area_area](#trap_area_area) |
| 1 | 25 | [trap_area_map_set](#trap_area_map_set) |
| 1 | 26 | [trap_area_battle_set](#trap_area_battle_set) |
| 1 | 27 | [trap_area_event_set](#trap_area_event_set) |
| 1 | 28 | [trap_obj_leave](#trap_obj_leave) |
| 1 | 29 | [trap_obj_motion_capture](#trap_obj_motion_capture) |
| 1 | 30 | [trap_area_jump](#trap_area_jump) |
| 1 | 31 | [trap_area_setjump](#trap_area_setjump) |
| 1 | 32 | [trap_message_open](#trap_message_open) |
| 1 | 33 | [trap_message_close](#trap_message_close) |
| 1 | 34 | [trap_event_is_exec](#trap_event_is_exec) |
| 1 | 35 | [trap_area_init](#trap_area_init) |
| 1 | 36 | [trap_bg_hide](#trap_bg_hide) |
| 1 | 37 | [trap_bg_show](#trap_bg_show) |
| 1 | 38 | [trap_obj_set_team](#trap_obj_set_team) |
| 1 | 39 | [trap_obj_unit_arg](#trap_obj_unit_arg) |
| 1 | 40 | [trap_obj_is_pirate_shade](#trap_obj_is_pirate_shade) |
| 1 | 41 | [trap_signal_call](#trap_signal_call) |
| 1 | 42 | [func_obj_control_off](#func_obj_control_off) |
| 1 | 43 | [func_obj_control_on](#func_obj_control_on) |
| 1 | 44 | [func_history_clear_enemy](#func_history_clear_enemy) |
| 1 | 45 | [func_area_activate_unit](#func_area_activate_unit) |
| 1 | 46 | [func_bg_barrier_on](#func_bg_barrier_on) |
| 1 | 47 | [func_bg_barrier_off](#func_bg_barrier_off) |
| 1 | 48 | [method_message_is_end](#method_message_is_end) |
| 1 | 49 | [method_obj_enable_reaction_command](#method_obj_enable_reaction_command) |
| 1 | 50 | [method_obj_disable_reaction_command](#method_obj_disable_reaction_command) |
| 1 | 51 | [method_obj_reset_reaction_command](#method_obj_reset_reaction_command) |
| 1 | 52 | [method_obj_enable_collision](#method_obj_enable_collision) |
| 1 | 53 | [method_obj_disable_collision](#method_obj_disable_collision) |
| 1 | 54 | [method_obj_reset_collision](#method_obj_reset_collision) |
| 1 | 55 | [method_obj_jump](#method_obj_jump) |
| 1 | 56 | [method_obj_is_culling](#method_obj_is_culling) |
| 1 | 57 | [trap_obj_is_jump](#trap_obj_is_jump) |
| 1 | 58 | [trap_obj_fly](#trap_obj_fly) |
| 1 | 59 | [trap_obj_is_fly](#trap_obj_is_fly) |
| 1 | 60 | [trap_obj_is_air](#trap_obj_is_air) |
| 1 | 61 | [trap_sysobj_motion_frame_start](#trap_sysobj_motion_frame_start) |
| 1 | 62 | [trap_obj_get_moved](#trap_obj_get_moved) |
| 1 | 63 | [trap_obj_is_motion_in_loop](#trap_obj_is_motion_in_loop) |
| 1 | 64 | [trap_obj_get_wish_movement](#trap_obj_get_wish_movement) |
| 1 | 65 | [trap_obj_exec_fall](#trap_obj_exec_fall) |
| 1 | 66 | [trap_obj_exec_land](#trap_obj_exec_land) |
| 1 | 67 | [trap_obj_motion_get_length](#trap_obj_motion_get_length) |
| 1 | 68 | [trap_obj_motion_get_loop_top](#trap_obj_motion_get_loop_top) |
| 1 | 69 | [trap_obj_motion_get_time](#trap_obj_motion_get_time) |
| 1 | 70 | [trap_obj_set_flag](#trap_obj_set_flag) |
| 1 | 71 | [trap_obj_reset_flag](#trap_obj_reset_flag) |
| 1 | 72 | [trap_obj_check_flag](#trap_obj_check_flag) |
| 1 | 73 | [trap_obj_hover](#trap_obj_hover) |
| 1 | 74 | [trap_obj_idle](#trap_obj_idle) |
| 1 | 75 | [trap_obj_motion_hook](#trap_obj_motion_hook) |
| 1 | 76 | [trap_obj_motion_unhook](#trap_obj_motion_unhook) |
| 1 | 77 | [trap_obj_motion_is_hook](#trap_obj_motion_is_hook) |
| 1 | 78 | [trap_obj_motion_is_no_control](#trap_obj_motion_is_no_control) |
| 1 | 79 | [trap_obj_set_dir](#trap_obj_set_dir) |
| 1 | 80 | [trap_obj_turn_dir](#trap_obj_turn_dir) |
| 1 | 81 | [trap_obj_act_wedge](#trap_obj_act_wedge) |
| 1 | 82 | [trap_obj_thread_start](#trap_obj_thread_start) |
| 1 | 83 | [trap_obj_apply_bone_matrix](#trap_obj_apply_bone_matrix) |
| 1 | 84 | [trap_obj_sheet](#trap_obj_sheet) |
| 1 | 85 | [trap_obj_texanm_start](#trap_obj_texanm_start) |
| 1 | 86 | [trap_obj_texanm_stop](#trap_obj_texanm_stop) |
| 1 | 87 | [trap_obj_effect_start_bind](#trap_obj_effect_start_bind) |
| 1 | 88 | [trap_obj_target_pos](#trap_obj_target_pos) |
| 1 | 89 | [trap_obj_move_request](#trap_obj_move_request) |
| 1 | 90 | [trap_obj_act_shout](#trap_obj_act_shout) |
| 1 | 91 | [trap_obj_star](#trap_obj_star) |
| 1 | 92 | [trap_obj_scatter_prize](#trap_obj_scatter_prize) |
| 1 | 93 | [trap_sysobj_party](#trap_sysobj_party) |
| 1 | 94 | [trap_sysobj_is_exist](#trap_sysobj_is_exist) |
| 1 | 95 | [trap_obj_fly_to_jump](#trap_obj_fly_to_jump) |
| 1 | 96 | [trap_obj_get_action](#trap_obj_get_action) |
| 1 | 97 | [trap_obj_spec](#trap_obj_spec) |
| 1 | 98 | [trap_obj_step_pos](#trap_obj_step_pos) |
| 1 | 99 | [trap_obj_float_height](#trap_obj_float_height) |
| 1 | 100 | [trap_obj_jump_height_to_uptime](#trap_obj_jump_height_to_uptime) |
| 1 | 101 | [trap_obj_motion_is_capture](#trap_obj_motion_is_capture) |
| 1 | 102 | [trap_obj_detach](#trap_obj_detach) |
| 1 | 103 | [trap_obj_set_detach_callback](#trap_obj_set_detach_callback) |
| 1 | 104 | [trap_obj_shadow_move_start](#trap_obj_shadow_move_start) |
| 1 | 105 | [trap_obj_shadow_move_end](#trap_obj_shadow_move_end) |
| 1 | 106 | [trap_signal_reserve_hp](#trap_signal_reserve_hp) |
| 1 | 107 | [trap_obj_motion_speed](#trap_obj_motion_speed) |
| 1 | 108 | [trap_obj_show_part](#trap_obj_show_part) |
| 1 | 109 | [trap_obj_hide_part](#trap_obj_hide_part) |
| 1 | 110 | [trap_obj_get_appear_way](#trap_obj_get_appear_way) |
| 1 | 111 | [trap_obj_set_movement](#trap_obj_set_movement) |
| 1 | 112 | [trap_obj_hook](#trap_obj_hook) |
| 1 | 113 | [trap_player_get_movement](#trap_player_get_movement) |
| 1 | 114 | [trap_obj_search_by_entry](#trap_obj_search_by_entry) |
| 1 | 115 | [trap_obj_set_jump_motion](#trap_obj_set_jump_motion) |
| 1 | 117 | [trap_command_cage_on](#trap_command_cage_on) |
| 1 | 118 | [trap_command_cage_off](#trap_command_cage_off) |
| 1 | 119 | [trap_obj_check_step](#trap_obj_check_step) |
| 1 | 120 | [trap_target_pos](#trap_target_pos) |
| 1 | 121 | [trap_target_search](#trap_target_search) |
| 1 | 122 | [trap_obj_dump](#trap_obj_dump) |
| 1 | 123 | [trap_obj_tex_fade_set](#trap_obj_tex_fade_set) |
| 1 | 124 | [trap_obj_is_entry_fly](#trap_obj_is_entry_fly) |
| 1 | 125 | [trap_obj_tex_fade_start](#trap_obj_tex_fade_start) |
| 1 | 126 | [trap_obj_motion_sync](#trap_obj_motion_sync) |
| 1 | 127 | [trap_obj_act_clear](#trap_obj_act_clear) |
| 1 | 128 | [trap_obj_sysjump](#trap_obj_sysjump) |
| 1 | 129 | [trap_obj_blow](#trap_obj_blow) |
| 1 | 130 | [trap_obj_cmp](#trap_obj_cmp) |
| 1 | 131 | [trap_target_dup](#trap_target_dup) |
| 1 | 132 | [trap_target_free](#trap_target_free) |
| 1 | 133 | [trap_obj_hide](#trap_obj_hide) |
| 1 | 134 | [trap_obj_show](#trap_obj_show) |
| 1 | 135 | [trap_bg_cross_pos](#trap_bg_cross_pos) |
| 1 | 136 | [trap_bg_is_floor](#trap_bg_is_floor) |
| 1 | 137 | [trap_bg_get_normal](#trap_bg_get_normal) |
| 1 | 138 | [trap_pax_start](#trap_pax_start) |
| 1 | 139 | [trap_pax_start_bind](#trap_pax_start_bind) |
| 1 | 140 | [trap_target_is_exist](#trap_target_is_exist) |
| 1 | 141 | [trap_bg_ground_pos](#trap_bg_ground_pos) |
| 1 | 142 | [trap_signal_reserve_min_hp](#trap_signal_reserve_min_hp) |
| 1 | 143 | [trap_obj_search_by_serial](#trap_obj_search_by_serial) |
| 1 | 144 | [trap_obj_serial](#trap_obj_serial) |
| 1 | 145 | [trap_obj_touch_zone](#trap_obj_touch_zone) |
| 1 | 146 | [trap_obj_hitback](#trap_obj_hitback) |
| 1 | 147 | [trap_obj_pos](#trap_obj_pos) |
| 1 | 148 | [trap_obj_set_pos](#trap_obj_set_pos) |
| 1 | 149 | [trap_obj_effect_start_bind_other](#trap_obj_effect_start_bind_other) |
| 1 | 150 | [trap_obj_motion_check_range](#trap_obj_motion_check_range) |
| 1 | 151 | [trap_obj_motion_check_trigger](#trap_obj_motion_check_trigger) |
| 1 | 152 | [trap_status_is_mission](#trap_status_is_mission) |
| 1 | 153 | [trap_obj_reset_pos](#trap_obj_reset_pos) |
| 1 | 154 | [trap_status_secure_mode_start](#trap_status_secure_mode_start) |
| 1 | 155 | [trap_obj_add_hp](#trap_obj_add_hp) |
| 1 | 156 | [trap_obj_hop](#trap_obj_hop) |
| 1 | 157 | [trap_obj_camera_start](#trap_obj_camera_start) |
| 1 | 158 | [trap_bg_set_belt_conveyor](#trap_bg_set_belt_conveyor) |
| 1 | 159 | [trap_bg_set_uvscroll_speed](#trap_bg_set_uvscroll_speed) |
| 1 | 160 | [trap_target_set_obj](#trap_target_set_obj) |
| 1 | 161 | [trap_obj_is_attach](#trap_obj_is_attach) |
| 1 | 162 | [trap_target_set_before_player](#trap_target_set_before_player) |
| 1 | 163 | [trap_target_set_after_player](#trap_target_set_after_player) |
| 1 | 164 | [trap_obj_camera_start_global](#trap_obj_camera_start_global) |
| 1 | 165 | [trap_command_override](#trap_command_override) |
| 1 | 166 | [trap_target_attack](#trap_target_attack) |
| 1 | 167 | [trap_obj_act_start_pri](#trap_obj_act_start_pri) |
| 1 | 168 | [trap_obj_flyjump](#trap_obj_flyjump) |
| 1 | 169 | [trap_obj_effect_unbind](#trap_obj_effect_unbind) |
| 1 | 170 | [trap_obj_unit_group](#trap_obj_unit_group) |
| 1 | 171 | [trap_status_no_leave](#trap_status_no_leave) |
| 1 | 172 | [trap_obj_can_look](#trap_obj_can_look) |
| 1 | 173 | [trap_obj_can_look_pos](#trap_obj_can_look_pos) |
| 1 | 174 | [trap_obj_look_start](#trap_obj_look_start) |
| 1 | 175 | [trap_obj_look_start_pos](#trap_obj_look_start_pos) |
| 1 | 176 | [trap_obj_look_end](#trap_obj_look_end) |
| 1 | 177 | [trap_obj_set_path](#trap_obj_set_path) |
| 1 | 178 | [trap_obj_get_path_movement](#trap_obj_get_path_movement) |
| 1 | 179 | [trap_obj_set_fall_motion](#trap_obj_set_fall_motion) |
| 1 | 180 | [trap_obj_set_land_motion](#trap_obj_set_land_motion) |
| 1 | 181 | [trap_light_create](#trap_light_create) |
| 1 | 182 | [trap_light_set_flag](#trap_light_set_flag) |
| 1 | 183 | [trap_light_set_color](#trap_light_set_color) |
| 1 | 184 | [trap_light_fadeout](#trap_light_fadeout) |
| 1 | 185 | [trap_obj_set_parts_color](#trap_obj_set_parts_color) |
| 1 | 186 | [trap_obj_reset_parts_color](#trap_obj_reset_parts_color) |
| 1 | 187 | [trap_status_prize_drain_start](#trap_status_prize_drain_start) |
| 1 | 188 | [trap_status_prize_drain_end](#trap_status_prize_drain_end) |
| 1 | 189 | [trap_obj_history_mark](#trap_obj_history_mark) |
| 1 | 190 | [trap_obj_is_history_mark](#trap_obj_is_history_mark) |
| 1 | 191 | [trap_obj_lockon_target](#trap_obj_lockon_target) |
| 1 | 192 | [trap_obj_is_motion_cancel](#trap_obj_is_motion_cancel) |
| 1 | 193 | [trap_camera_warp](#trap_camera_warp) |
| 1 | 194 | [trap_obj_set_stealth](#trap_obj_set_stealth) |
| 1 | 195 | [trap_obj_reset_stealth](#trap_obj_reset_stealth) |
| 1 | 196 | [trap_area_entrance](#trap_area_entrance) |
| 1 | 197 | [trap_area_cost_rest](#trap_area_cost_rest) |
| 1 | 198 | [trap_obj_set_player_random_pos](#trap_obj_set_player_random_pos) |
| 1 | 199 | [trap_obj_set_random_pos](#trap_obj_set_random_pos) |
| 1 | 200 | [trap_obj_set_bg_collision_type](#trap_obj_set_bg_collision_type) |
| 1 | 201 | [trap_obj_dir](#trap_obj_dir) |
| 1 | 202 | [trap_unit_disable](#trap_unit_disable) |
| 1 | 203 | [trap_unit_enable](#trap_unit_enable) |
| 1 | 204 | [trap_status_force_leave_start](#trap_status_force_leave_start) |
| 1 | 205 | [trap_status_force_leave_end](#trap_status_force_leave_end) |
| 1 | 206 | [trap_status_is_force_leave](#trap_status_is_force_leave) |
| 1 | 207 | [trap_camera_watch](#trap_camera_watch) |
| 1 | 208 | [trap_obj_is_hover](#trap_obj_is_hover) |
| 1 | 209 | [trap_obj_dead](#trap_obj_dead) |
| 1 | 210 | [trap_obj_search_by_part](#trap_obj_search_by_part) |
| 1 | 211 | [trap_obj_pattern_enable](#trap_obj_pattern_enable) |
| 1 | 212 | [trap_obj_pattern_disable](#trap_obj_pattern_disable) |
| 1 | 213 | [trap_obj_part](#trap_obj_part) |
| 1 | 214 | [trap_obj_hook_stop](#trap_obj_hook_stop) |
| 1 | 217 | [trap_obj_set_pos_trans](#trap_obj_set_pos_trans) |
| 1 | 218 | [trap_obj_set_unit_arg](#trap_obj_set_unit_arg) |
| 1 | 219 | [trap_obj_camera_start](#trap_obj_camera_start) |
| 1 | 220 | [trap_obj_move_to_space](#trap_obj_move_to_space) |
| 1 | 221 | [trap_obj_can_decide_command](#trap_obj_can_decide_command) |
| 1 | 222 | [trap_obj_get_entry_id](#trap_obj_get_entry_id) |
| 1 | 223 | [trap_camera_cancel](#trap_camera_cancel) |
| 1 | 224 | [trap_obj_is_action_air](#trap_obj_is_action_air) |
| 1 | 225 | [trap_obj_is_star](#trap_obj_is_star) |
| 1 | 226 | [trap_obj_scatter_prize_mu](#trap_obj_scatter_prize_mu) |
| 1 | 227 | [trap_obj_jump_direct](#trap_obj_jump_direct) |
| 1 | 228 | [trap_sheet_hp](#trap_sheet_hp) |
| 1 | 229 | [trap_sheet_max_hp](#trap_sheet_max_hp) |
| 1 | 230 | [trap_sheet_hp_rate](#trap_sheet_hp_rate) |
| 1 | 231 | [trap_sheet_set_min_hp](#trap_sheet_set_min_hp) |
| 1 | 232 | [trap_sheet_min_hp](#trap_sheet_min_hp) |
| 1 | 233 | [trap_sheet_set_hp](#trap_sheet_set_hp) |
| 1 | 234 | [trap_party_get_weapon](#trap_party_get_weapon) |
| 1 | 235 | [trap_party_hand_to_bone](#trap_party_hand_to_bone) |
| 1 | 236 | [trap_obj_motion_unsync](#trap_obj_motion_unsync) |
| 1 | 237 | [trap_command_override_top](#trap_command_override_top) |
| 1 | 238 | [trap_obj_motion_capture_id](#trap_obj_motion_capture_id) |
| 1 | 239 | [trap_obj_is_unit_active](#trap_obj_is_unit_active) |
| 1 | 240 | [trap_obj_scatter_prize_tt](#trap_obj_scatter_prize_tt) |
| 1 | 241 | [trap_act_shout](#trap_act_shout) |
| 1 | 242 | [trap_player_capture_form](#trap_player_capture_form) |
| 1 | 243 | [trap_player_capture_form_end](#trap_player_capture_form_end) |
| 1 | 244 | [trap_status_is_battle](#trap_status_is_battle) |
| 1 | 245 | [trap_target_clear_before_player](#trap_target_clear_before_player) |
| 1 | 246 | [trap_target_clear_after_player](#trap_target_clear_after_player) |
| 1 | 247 | [trap_bg_get_random_pos](#trap_bg_get_random_pos) |
| 1 | 248 | [trap_bg_get_random_pos_air](#trap_bg_get_random_pos_air) |
| 1 | 249 | [trap_status_set_prize_ratio](#trap_status_set_prize_ratio) |
| 1 | 250 | [trap_status_set_lockon_ratio](#trap_status_set_lockon_ratio) |
| 1 | 251 | [trap_light_fadein](#trap_light_fadein) |
| 1 | 252 | [trap_camera_apply_pos](#trap_camera_apply_pos) |
| 1 | 253 | [trap_obj_can_capture_control](#trap_obj_can_capture_control) |
| 1 | 254 | [trap_obj_is_ride](#trap_obj_is_ride) |
| 1 | 255 | [trap_obj_disable_occ](#trap_obj_disable_occ) |
| 1 | 256 | [trap_obj_enable_occ](#trap_obj_enable_occ) |
| 1 | 257 | [trap_light_set_fog_near](#trap_light_set_fog_near) |
| 1 | 258 | [trap_light_set_fog_far](#trap_light_set_fog_far) |
| 1 | 259 | [trap_light_set_fog_min](#trap_light_set_fog_min) |
| 1 | 260 | [trap_light_set_fog_max](#trap_light_set_fog_max) |
| 1 | 261 | [trap_sheet_munny](#trap_sheet_munny) |
| 1 | 262 | [trap_obj_voice](#trap_obj_voice) |
| 1 | 263 | [trap_player_set_exec_rc](#trap_player_set_exec_rc) |
| 1 | 264 | [trap_status_secure_mode_end](#trap_status_secure_mode_end) |
| 1 | 265 | [trap_obj_set_medal](#trap_obj_set_medal) |
| 1 | 266 | [trap_obj_get_medal](#trap_obj_get_medal) |
| 1 | 267 | [trap_obj_scatter_medal](#trap_obj_scatter_medal) |
| 1 | 268 | [trap_obj_action_lightcycle](#trap_obj_action_lightcycle) |
| 1 | 269 | [trap_obj_get_lightcycle_movement](#trap_obj_get_lightcycle_movement) |
| 1 | 270 | [trap_obj_motion_disable_anmatr_effect](#trap_obj_motion_disable_anmatr_effect) |
| 1 | 271 | [trap_obj_motion_enable_anmatr_effect](#trap_obj_motion_enable_anmatr_effect) |
| 1 | 272 | [trap_obj_is_dead](#trap_obj_is_dead) |
| 1 | 273 | [trap_signal_hook](#trap_signal_hook) |
| 1 | 274 | [trap_event_get_rest_time](#trap_event_get_rest_time) |
| 1 | 275 | [trap_obj_recov_holylight](#trap_obj_recov_holylight) |
| 1 | 276 | [trap_obj_use_mp](#trap_obj_use_mp) |
| 1 | 277 | [trap_obj_reraise](#trap_obj_reraise) |
| 1 | 278 | [trap_obj_scatter_prize_tr](#trap_obj_scatter_prize_tr) |
| 1 | 279 | [trap_prize_appear_tr](#trap_prize_appear_tr) |
| 1 | 280 | [trap_sheet_add_munny](#trap_sheet_add_munny) |
| 1 | 281 | [trap_camera_begin_scope](#trap_camera_begin_scope) |
| 1 | 283 | [trap_camera_end_scope](#trap_camera_end_scope) |
| 1 | 284 | [trap_tutorial_pause](#trap_tutorial_pause) |
| 1 | 285 | [trap_obj_show_picture](#trap_obj_show_picture) |
| 1 | 286 | [trap_status_hide_shadow](#trap_status_hide_shadow) |
| 1 | 287 | [trap_status_show_shadow](#trap_status_show_shadow) |
| 1 | 288 | [trap_status_begin_free_ability](#trap_status_begin_free_ability) |
| 1 | 289 | [trap_status_end_free_ability](#trap_status_end_free_ability) |
| 1 | 290 | [trap_picture_change](#trap_picture_change) |
| 1 | 291 | [trap_obj_levelup_unit](#trap_obj_levelup_unit) |
| 1 | 292 | [trap_obj_search_by_unit_arg](#trap_obj_search_by_unit_arg) |
| 1 | 293 | [trap_event_control_off](#trap_event_control_off) |
| 1 | 294 | [trap_event_control_on](#trap_event_control_on) |
| 1 | 295 | [trap_camera_reset](#trap_camera_reset) |
| 1 | 296 | [trap_tutorial_open](#trap_tutorial_open) |
| 1 | 297 | [trap_player_get_rc](#trap_player_get_rc) |
| 1 | 298 | [trap_worldwork_get](#trap_worldwork_get) |
| 1 | 299 | [trap_area_set_next_entrance](#trap_area_set_next_entrance) |
| 1 | 300 | [trap_prize_num](#trap_prize_num) |
| 1 | 301 | [trap_tutorial_is_open](#trap_tutorial_is_open) |
| 1 | 302 | [trap_obj_set_skateboard_mode](#trap_obj_set_skateboard_mode) |
| 1 | 303 | [trap_area_cost_ratio](#trap_area_cost_ratio) |
| 1 | 304 | [trap_obj_search_by_glance](#trap_obj_search_by_glance) |
| 1 | 305 | [trap_camera_eye](#trap_camera_eye) |
| 1 | 306 | [trap_camera_at](#trap_camera_at) |
| 1 | 307 | [trap_obj_search_by_camera](#trap_obj_search_by_camera) |
| 1 | 308 | [trap_obj_capture_command](#trap_obj_capture_command) |
| 1 | 309 | [trap_sysobj_is_player](#trap_sysobj_is_player) |
| 1 | 310 | [trap_obj_get_weight](#trap_obj_get_weight) |
| 1 | 311 | [trap_sheet_set_element_rate](#trap_sheet_set_element_rate) |
| 1 | 312 | [trap_camera_set_scope_zoom](#trap_camera_set_scope_zoom) |
| 1 | 313 | [trap_camera_set_scope_closeup_distance](#trap_camera_set_scope_closeup_distance) |
| 1 | 314 | [trap_camera_set_scope_target_pos](#trap_camera_set_scope_target_pos) |
| 1 | 315 | [trap_picture_set_pos](#trap_picture_set_pos) |
| 1 | 316 | [trap_camera_get_projection_pos](#trap_camera_get_projection_pos) |
| 1 | 317 | [trap_status_no_gameover](#trap_status_no_gameover) |
| 1 | 318 | [trap_obj_play_se](#trap_obj_play_se) |
| 1 | 319 | [trap_sysobj_is_sora](#trap_sysobj_is_sora) |
| 1 | 320 | [trap_unit_get_enemy_num](#trap_unit_get_enemy_num) |
| 1 | 321 | [trap_player_lockon](#trap_player_lockon) |
| 1 | 322 | [trap_command_enable_item](#trap_command_enable_item) |
| 1 | 323 | [trap_obj_count_entry](#trap_obj_count_entry) |
| 1 | 324 | [trap_obj_pattern_reset](#trap_obj_pattern_reset) |
| 1 | 325 | [trap_obj_reaction_callback](#trap_obj_reaction_callback) |
| 1 | 326 | [trap_bg_set_animation_speed](#trap_bg_set_animation_speed) |
| 1 | 327 | [trap_prize_get_all_tr](#trap_prize_get_all_tr) |
| 1 | 328 | [trap_obj_dead_mark](#trap_obj_dead_mark) |
| 1 | 329 | [trap_sheet_set_prize_range](#trap_sheet_set_prize_range) |
| 1 | 330 | [trap_obj_set_cannon_camera_offset](#trap_obj_set_cannon_camera_offset) |
| 1 | 331 | [trap_obj_each_all](#trap_obj_each_all) |
| 1 | 332 | [trap_sysobj_is_btlnpc](#trap_sysobj_is_btlnpc) |
| 1 | 333 | [trap_obj_set_cannon_param](#trap_obj_set_cannon_param) |
| 1 | 334 | [trap_command_enable](#trap_command_enable) |
| 1 | 335 | [trap_obj_disable_occ_bone](#trap_obj_disable_occ_bone) |
| 1 | 336 | [trap_obj_enable_occ_bone](#trap_obj_enable_occ_bone) |
| 1 | 337 | [trap_command_set_side_b](#trap_command_set_side_b) |
| 1 | 338 | [trap_prize_return_ca](#trap_prize_return_ca) |
| 1 | 339 | [trap_prize_vacuum_ca](#trap_prize_vacuum_ca) |
| 1 | 340 | [trap_prize_vacuum_range_ca](#trap_prize_vacuum_range_ca) |
| 1 | 341 | [trap_prize_num_ca](#trap_prize_num_ca) |
| 1 | 342 | [trap_prize_appear_num](#trap_prize_appear_num) |
| 1 | 343 | [trap_obj_is_equip_ability](#trap_obj_is_equip_ability) |
| 1 | 344 | [trap_obj_clear_occ](#trap_obj_clear_occ) |
| 1 | 345 | [trap_command_override_slot](#trap_command_override_slot) |
| 1 | 346 | [trap_command_slot_set_status](#trap_command_slot_set_status) |
| 1 | 347 | [trap_obj_can_see](#trap_obj_can_see) |
| 1 | 348 | [trap_sheet_set_hitback_addition](#trap_sheet_set_hitback_addition) |
| 1 | 349 | [trap_obj_effect_kill_all](#trap_obj_effect_kill_all) |
| 1 | 350 | [trap_status_close_pete_curtain](#trap_status_close_pete_curtain) |
| 1 | 351 | [trap_status_open_pete_curtain](#trap_status_open_pete_curtain) |
| 1 | 352 | [trap_area_set_return_tr](#trap_area_set_return_tr) |
| 1 | 353 | [trap_obj_start_mpdrive](#trap_obj_start_mpdrive) |
| 1 | 354 | [trap_event_layer_off](#trap_event_layer_off) |
| 1 | 355 | [trap_player_can_capture_form](#trap_player_can_capture_form) |
| 1 | 356 | [trap_event_layer_on](#trap_event_layer_on) |
| 1 | 357 | [trap_sheet_attack_level](#trap_sheet_attack_level) |
| 1 | 358 | [trap_sheet_set_attack_level](#trap_sheet_set_attack_level) |
| 1 | 359 | [trap_obj_hook_command_image](#trap_obj_hook_command_image) |
| 1 | 360 | [trap_obj_reset_command_image](#trap_obj_reset_command_image) |
| 1 | 361 | [trap_sheet_level](#trap_sheet_level) |
| 1 | 362 | [trap_treasure_get](#trap_treasure_get) |
| 1 | 363 | [trap_prize_appear_xaldin](#trap_prize_appear_xaldin) |
| 1 | 364 | [trap_jigsaw_get](#trap_jigsaw_get) |
| 1 | 365 | [trap_command_disable_group](#trap_command_disable_group) |
| 1 | 366 | [trap_command_enable_group](#trap_command_enable_group) |
| 1 | 367 | [trap_obj_get_move_to_space_pos](#trap_obj_get_move_to_space_pos) |
| 2 | 0 | [trap_enemy_exec_damage](#trap_enemy_exec_damage) |
| 2 | 1 | [trap_enemy_exec_damage_blow](#trap_enemy_exec_damage_blow) |
| 2 | 2 | [trap_enemy_exec_damage_small](#trap_enemy_exec_damage_small) |
| 2 | 3 | [trap_enemy_exec_damage_hitback](#trap_enemy_exec_damage_hitback) |
| 2 | 4 | [trap_enemy_each](#trap_enemy_each) |
| 2 | 5 | [trap_enemy_is_no_control](#trap_enemy_is_no_control) |
| 2 | 6 | [trap_enemy_is_damage_motion](#trap_enemy_is_damage_motion) |
| 2 | 7 | [trap_damage_reaction](#trap_damage_reaction) |
| 2 | 8 | [trap_damage_is_reaction](#trap_damage_is_reaction) |
| 2 | 9 | [trap_btlobj_set_sheet](#trap_btlobj_set_sheet) |
| 2 | 10 | [trap_attack_new](#trap_attack_new) |
| 2 | 11 | [trap_attack_set_radius](#trap_attack_set_radius) |
| 2 | 12 | [trap_attack_set_pos](#trap_attack_set_pos) |
| 2 | 13 | [trap_attack_free](#trap_attack_free) |
| 2 | 14 | [trap_attack_is_hit](#trap_attack_is_hit) |
| 2 | 15 | [trap_damage_exec_reaction](#trap_damage_exec_reaction) |
| 2 | 16 | [trap_damage_is_exec_reaction](#trap_damage_is_exec_reaction) |
| 2 | 17 | [trap_attack_strike](#trap_attack_strike) |
| 2 | 18 | [trap_attack_is_strike](#trap_attack_is_strike) |
| 2 | 19 | [trap_attack_set_line](#trap_attack_set_line) |
| 2 | 20 | [trap_magic_start_thread](#trap_magic_start_thread) |
| 2 | 21 | [trap_teamwork_alloc](#trap_teamwork_alloc) |
| 2 | 22 | [trap_attack_set_obj_pax](#trap_attack_set_obj_pax) |
| 2 | 23 | [trap_btlobj_target](#trap_btlobj_target) |
| 2 | 24 | [trap_attack_get_owner](#trap_attack_get_owner) |
| 2 | 25 | [trap_attack_get_param_id](#trap_attack_get_param_id) |
| 2 | 26 | [trap_attack_exec_reflect](#trap_attack_exec_reflect) |
| 2 | 27 | [trap_enemy_exec_reflect](#trap_enemy_exec_reflect) |
| 2 | 28 | [trap_attack_refresh](#trap_attack_refresh) |
| 2 | 29 | [trap_attack_is_hit_bg](#trap_attack_is_hit_bg) |
| 2 | 30 | [trap_attack_set_pax](#trap_attack_set_pax) |
| 2 | 31 | [trap_attack_dup](#trap_attack_dup) |
| 2 | 32 | [trap_damage_blow_up](#trap_damage_blow_up) |
| 2 | 33 | [trap_damage_blow_speed](#trap_damage_blow_speed) |
| 2 | 34 | [trap_attack_get_type](#trap_attack_get_type) |
| 2 | 35 | [trap_damage_attack_type](#trap_damage_attack_type) |
| 2 | 36 | [trap_enemy_add_damage](#trap_enemy_add_damage) |
| 2 | 37 | [trap_attack_set_team](#trap_attack_set_team) |
| 2 | 38 | [trap_attack_set_hit_callback](#trap_attack_set_hit_callback) |
| 2 | 39 | [trap_attack_is_reflect](#trap_attack_is_reflect) |
| 2 | 40 | [trap_attack_is_hit_wall](#trap_attack_is_hit_wall) |
| 2 | 41 | [trap_attack_is_hit_floor](#trap_attack_is_hit_floor) |
| 2 | 42 | [trap_attack_hit_bg_pos](#trap_attack_hit_bg_pos) |
| 2 | 43 | [trap_attack_get_reflect_vector](#trap_attack_get_reflect_vector) |
| 2 | 44 | [trap_attack_reflecter](#trap_attack_reflecter) |
| 2 | 45 | [trap_damage_attack_param_id](#trap_damage_attack_param_id) |
| 2 | 46 | [trap_damage_damage](#trap_damage_damage) |
| 2 | 47 | [trap_limit_motion_start](#trap_limit_motion_start) |
| 2 | 48 | [trap_limit_player](#trap_limit_player) |
| 2 | 49 | [trap_limit_friend](#trap_limit_friend) |
| 2 | 50 | [trap_limit_camera_start](#trap_limit_camera_start) |
| 2 | 51 | [trap_attack_set_rc](#trap_attack_set_rc) |
| 2 | 52 | [trap_attack_rc_receiver](#trap_attack_rc_receiver) |
| 2 | 53 | [trap_enemy_last_dead](#trap_enemy_last_dead) |
| 2 | 54 | [trap_limit_start_thread](#trap_limit_start_thread) |
| 2 | 55 | [trap_limit_light](#trap_limit_light) |
| 2 | 56 | [trap_btlobj_lockon_target](#trap_btlobj_lockon_target) |
| 2 | 57 | [trap_limit_effect_start](#trap_limit_effect_start) |
| 2 | 58 | [trap_limit_effect_start_pos](#trap_limit_effect_start_pos) |
| 2 | 59 | [trap_limit_effect_start_bind](#trap_limit_effect_start_bind) |
| 2 | 60 | [trap_limit_time](#trap_limit_time) |
| 2 | 61 | [trap_attack_set_effect](#trap_attack_set_effect) |
| 2 | 62 | [trap_attack_set_time](#trap_attack_set_time) |
| 2 | 63 | [trap_limit_reference](#trap_limit_reference) |
| 2 | 64 | [trap_damage_orig_reaction](#trap_damage_orig_reaction) |
| 2 | 65 | [trap_enemy_count_damager](#trap_enemy_count_damager) |
| 2 | 66 | [trap_attack_get_reflect_count](#trap_attack_get_reflect_count) |
| 2 | 67 | [trap_attack_new_combo_group](#trap_attack_new_combo_group) |
| 2 | 68 | [trap_magic_set_cost](#trap_magic_set_cost) |
| 2 | 69 | [trap_magic_can_add_cost](#trap_magic_can_add_cost) |
| 2 | 70 | [trap_damage_parts](#trap_damage_parts) |
| 2 | 71 | [trap_attack_set_hitmark_pos](#trap_attack_set_hitmark_pos) |
| 2 | 72 | [trap_damage_is_cure](#trap_damage_is_cure) |
| 2 | 73 | [trap_bonuslevel_up](#trap_bonuslevel_up) |
| 2 | 74 | [trap_attack_set_reflect_callback](#trap_attack_set_reflect_callback) |
| 2 | 75 | [trap_summon_is_tink_exist](#trap_summon_is_tink_exist) |
| 2 | 76 | [trap_enemy_set_karma_limit](#trap_enemy_set_karma_limit) |
| 2 | 77 | [trap_vacuum_create](#trap_vacuum_create) |
| 2 | 78 | [trap_vacuum_destroy](#trap_vacuum_destroy) |
| 2 | 79 | [trap_vacuum_set_ignore_type](#trap_vacuum_set_ignore_type) |
| 2 | 80 | [trap_vacuum_set_pos](#trap_vacuum_set_pos) |
| 2 | 81 | [trap_vacuum_set_speed](#trap_vacuum_set_speed) |
| 2 | 82 | [trap_vacuum_set_rot_speed](#trap_vacuum_set_rot_speed) |
| 2 | 83 | [trap_vacuum_set_near_range](#trap_vacuum_set_near_range) |
| 2 | 84 | [trap_vacuum_set_dist_rate](#trap_vacuum_set_dist_rate) |
| 2 | 85 | [trap_damage_element](#trap_damage_element) |
| 2 | 86 | [trap_damage_get_hitback](#trap_damage_get_hitback) |
| 2 | 87 | [trap_enemy_exec_damage_large](#trap_enemy_exec_damage_large) |
| 2 | 88 | [trap_enemy_get_attacker](#trap_enemy_get_attacker) |
| 2 | 89 | [trap_limit_reset_special_command](#trap_limit_reset_special_command) |
| 2 | 90 | [trap_limit_close_gauge](#trap_limit_close_gauge) |
| 2 | 91 | [trap_damage_get_reaction_type](#trap_damage_get_reaction_type) |
| 2 | 92 | [trap_damage_is_finish](#trap_damage_is_finish) |
| 2 | 93 | [trap_damage_is_normal](#trap_damage_is_normal) |
| 2 | 94 | [trap_attack_set_system_pax](#trap_attack_set_system_pax) |
| 2 | 95 | [trap_btlobj_dup_sheet](#trap_btlobj_dup_sheet) |
| 2 | 96 | [trap_attack_is_valid](#trap_attack_is_valid) |
| 2 | 97 | [trap_enemy_set_attacker](#trap_enemy_set_attacker) |
| 4 | 2 | [trap_event_is_exec](#trap_event_is_exec) |
| 4 | 3 | [trap_mission_complete](#trap_mission_complete) |
| 4 | 4 | [trap_mission_information](#trap_mission_information) |
| 4 | 5 | [trap_mission_set_count](#trap_mission_set_count) |
| 4 | 6 | [trap_mission_increment_count](#trap_mission_increment_count) |
| 4 | 7 | [trap_mission_restart_timer](#trap_mission_restart_timer) |
| 4 | 8 | [trap_mission_set_gauge](#trap_mission_set_gauge) |
| 4 | 9 | [trap_mission_add_gauge](#trap_mission_add_gauge) |
| 4 | 10 | [trap_mission_set_gauge_ratio](#trap_mission_set_gauge_ratio) |
| 4 | 11 | [trap_mission_failed](#trap_mission_failed) |
| 4 | 12 | [trap_mission_get_gauge_ratio](#trap_mission_get_gauge_ratio) |
| 4 | 13 | [trap_mission_pause_timer](#trap_mission_pause_timer) |
| 4 | 14 | [trap_mission_activate2d](#trap_mission_activate2d) |
| 4 | 15 | [trap_mission_deactivate2d](#trap_mission_deactivate2d) |
| 4 | 16 | [trap_mission_dead_boss](#trap_mission_dead_boss) |
| 4 | 17 | [trap_mission_set_timer_param](#trap_mission_set_timer_param) |
| 4 | 18 | [trap_mission_set_count_param](#trap_mission_set_count_param) |
| 4 | 19 | [trap_mission_set_gauge_param](#trap_mission_set_gauge_param) |
| 4 | 20 | [trap_mission_decrement_count](#trap_mission_decrement_count) |
| 4 | 21 | [trap_mission_is_activate2d](#trap_mission_is_activate2d) |
| 4 | 22 | [trap_mission_exit](#trap_mission_exit) |
| 4 | 23 | [trap_mission_reset_pause_mode](#trap_mission_reset_pause_mode) |
| 4 | 24 | [trap_mission_cancel_pause_timer](#trap_mission_cancel_pause_timer) |
| 4 | 25 | [trap_mission_start_combo_counter](#trap_mission_start_combo_counter) |
| 4 | 26 | [trap_mission_get_timer](#trap_mission_get_timer) |
| 4 | 27 | [trap_mission_stop_combo_counter](#trap_mission_stop_combo_counter) |
| 4 | 28 | [trap_mission_get_gauge_warning_ratio](#trap_mission_get_gauge_warning_ratio) |
| 4 | 29 | [trap_mission_get_count](#trap_mission_get_count) |
| 4 | 30 | [trap_mission_get_max_combo_counter](#trap_mission_get_max_combo_counter) |
| 4 | 31 | [trap_mission_get_combo_counter](#trap_mission_get_combo_counter) |
| 4 | 32 | [trap_mission_return](#trap_mission_return) |
| 4 | 33 | [trap_mission_add_combo_counter](#trap_mission_add_combo_counter) |
| 4 | 34 | [trap_mission_is_gauge_warning](#trap_mission_is_gauge_warning) |
| 4 | 35 | [trap_score_type](#trap_score_type) |
| 4 | 36 | [trap_score_score](#trap_score_score) |
| 4 | 37 | [trap_score_update](#trap_score_update) |
| 4 | 38 | [trap_score_get](#trap_score_get) |
| 4 | 39 | [trap_mission_set_watch](#trap_mission_set_watch) |
| 4 | 40 | [trap_mission_get_timer_second](#trap_mission_get_timer_second) |
| 4 | 41 | [trap_mission_add_count](#trap_mission_add_count) |
| 4 | 42 | [trap_struggle_increment](#trap_struggle_increment) |
| 4 | 43 | [trap_mission_set_max_combo_counter](#trap_mission_set_max_combo_counter) |
| 4 | 44 | [trap_mission_disable_count](#trap_mission_disable_count) |
| 4 | 45 | [trap_mission_disable_watch](#trap_mission_disable_watch) |
| 4 | 46 | [trap_mission_set_warning_se](#trap_mission_set_warning_se) |
| 4 | 47 | [trap_mission_warning_timer](#trap_mission_warning_timer) |
| 4 | 48 | [trap_mission_set_count_figure_num](#trap_mission_set_count_figure_num) |
| 4 | 49 | [trap_mission_disable_timer](#trap_mission_disable_timer) |
| 4 | 50 | [trap_mission_warning_count](#trap_mission_warning_count) |
| 4 | 51 | [trap_mission_set_combo_counter_param](#trap_mission_set_combo_counter_param) |
| 4 | 52 | [trap_mission_warning_combo_counter](#trap_mission_warning_combo_counter) |
| 4 | 53 | [trap_mission_set_combo_counter_warning_se](#trap_mission_set_combo_counter_warning_se) |
| 4 | 54 | [trap_mission_lock](#trap_mission_lock) |
| 4 | 55 | [trap_mission_is_lock](#trap_mission_is_lock) |
| 4 | 56 | [trap_event_continue_control_off](#trap_event_continue_control_off) |
| 4 | 57 | [trap_mission_warning_gauge](#trap_mission_warning_gauge) |
| 4 | 58 | [trap_mission_reset_warning_count](#trap_mission_reset_warning_count) |
| 5 | 0 | [trap_get_start_rtn_action](#trap_get_start_rtn_action) |
| 5 | 1 | [trap_set_path_way](#trap_set_path_way) |
| 5 | 2 | [trap_reverse_path_way](#trap_reverse_path_way) |
| 5 | 3 | [trap_get_path_dir](#trap_get_path_dir) |
| 5 | 4 | [trap_end_rtn_action](#trap_end_rtn_action) |
| 5 | 5 | [trap_get_rtn_action](#trap_get_rtn_action) |
| 5 | 6 | [trap_get_rtn_action_dir](#trap_get_rtn_action_dir) |
| 5 | 7 | [trap_is_rtn_change_dir](#trap_is_rtn_change_dir) |
| 5 | 8 | [trap_create_active_path](#trap_create_active_path) |
| 5 | 9 | [trap_get_path_dir_from_obj](#trap_get_path_dir_from_obj) |
| 5 | 10 | [trap_forward_path_current_pointer](#trap_forward_path_current_pointer) |
| 5 | 11 | [trap_is_end_rtn_action](#trap_is_end_rtn_action) |
| 5 | 12 | [trap_reset_active_path](#trap_reset_active_path) |
| 5 | 13 | [trap_set_path_target_point](#trap_set_path_target_point) |
| 5 | 14 | [trap_get_path_point_pos](#trap_get_path_point_pos) |
| 5 | 15 | [trap_clear_active_path](#trap_clear_active_path) |
| 5 | 16 | [trap_reset_leave_way](#trap_reset_leave_way) |
| 5 | 17 | [trap_check_rtn_option_flag](#trap_check_rtn_option_flag) |
| 5 | 18 | [trap_reset_path_current_pointer](#trap_reset_path_current_pointer) |
| 5 | 19 | [trap_get_path_current_pos](#trap_get_path_current_pos) |
| 5 | 20 | [trap_get_path_current_dir](#trap_get_path_current_dir) |
| 5 | 21 | [trap_get_path_first_point_pos](#trap_get_path_first_point_pos) |
| 5 | 22 | [trap_get_path_last_point_pos](#trap_get_path_last_point_pos) |
| 5 | 23 | [trap_set_path_by_id](#trap_set_path_by_id) |
| 5 | 24 | [trap_set_path_by_group](#trap_set_path_by_group) |
| 5 | 25 | [trap_get_path_dir_r](#trap_get_path_dir_r) |
| 5 | 26 | [trap_set_rtn_partner](#trap_set_rtn_partner) |
| 5 | 27 | [trap_set_rtn_option_flag](#trap_set_rtn_option_flag) |
| 5 | 28 | [trap_eh22_path_move_next](#trap_eh22_path_move_next) |
| 5 | 29 | [trap_eh22_path_move_before](#trap_eh22_path_move_before) |
| 5 | 30 | [trap_eh22_path_is_moving](#trap_eh22_path_is_moving) |
| 5 | 31 | [trap_eh22_path_get_point](#trap_eh22_path_get_point) |
| 5 | 32 | [trap_eh22_path_play](#trap_eh22_path_play) |
| 5 | 33 | [trap_set_rtn_time_param](#trap_set_rtn_time_param) |
| 5 | 34 | [trap_get_obj_head_pos](#trap_get_obj_head_pos) |
| 6 | 0 | [trap_camera_shake](#trap_camera_shake) |
| 6 | 1 | [trap_prize_appear](#trap_prize_appear) |
| 6 | 2 | [trap_player_get_form](#trap_player_get_form) |
| 6 | 3 | [trap_target_searcher_init](#trap_target_searcher_init) |
| 6 | 4 | [trap_target_searcher_reset](#trap_target_searcher_reset) |
| 6 | 5 | [trap_target_seracher_search](#trap_target_seracher_search) |
| 6 | 6 | [trap_obj_stop](#trap_obj_stop) |
| 6 | 7 | [trap_obj_restart](#trap_obj_restart) |
| 6 | 8 | [trap_target_searcher_add](#trap_target_searcher_add) |
| 6 | 9 | [trap_target_dist](#trap_target_dist) |
| 6 | 10 | [trap_obj_is_hit_attack](#trap_obj_is_hit_attack) |
| 6 | 11 | [trap_target_searcher_search_obj](#trap_target_searcher_search_obj) |
| 6 | 12 | [trap_target_searcher_get_old](#trap_target_searcher_get_old) |
| 6 | 13 | [trap_friend_force_warp](#trap_friend_force_warp) |
| 6 | 14 | [trap_friend_get](#trap_friend_get) |
| 6 | 15 | [trap_friend_set_warp_level](#trap_friend_set_warp_level) |
| 6 | 16 | [trap_target_clear](#trap_target_clear) |
| 6 | 17 | [trap_lockon_show](#trap_lockon_show) |
| 6 | 18 | [trap_lockon_hide](#trap_lockon_hide) |
| 6 | 19 | [trap_status_peterpan_prize_drain_start](#trap_status_peterpan_prize_drain_start) |
| 6 | 20 | [trap_status_peterpan_prize_drain_end](#trap_status_peterpan_prize_drain_end) |
| 6 | 21 | [trap_target_searcher_add_target](#trap_target_searcher_add_target) |
| 6 | 22 | [trap_target_searcher_get_target_num](#trap_target_searcher_get_target_num) |
| 6 | 23 | [trap_obj_near_parts](#trap_obj_near_parts) |
| 6 | 24 | [trap_obj_get_bg_press](#trap_obj_get_bg_press) |
| 6 | 25 | [trap_obj_tt_ball_blow](#trap_obj_tt_ball_blow) |
| 6 | 26 | [trap_obj_limit_hover](#trap_obj_limit_hover) |
| 6 | 27 | [trap_player_dice](#trap_player_dice) |
| 6 | 28 | [trap_dice_set_spec](#trap_dice_set_spec) |
| 6 | 29 | [trap_player_card](#trap_player_card) |
| 6 | 30 | [trap_card_set_spec](#trap_card_set_spec) |
| 6 | 31 | [trap_limit_aladdin_prize_drain](#trap_limit_aladdin_prize_drain) |
| 6 | 32 | [trap_skateboard_ride](#trap_skateboard_ride) |
| 6 | 33 | [trap_skateboard_trick](#trap_skateboard_trick) |
| 6 | 34 | [trap_skateboard_trick_motion_push](#trap_skateboard_trick_motion_push) |
| 6 | 35 | [trap_obj_attach_camera](#trap_obj_attach_camera) |
| 6 | 36 | [trap_obj_detach_camera](#trap_obj_detach_camera) |
| 6 | 37 | [trap_obj_is_attach_camera](#trap_obj_is_attach_camera) |
| 6 | 38 | [trap_obj_limit_mulan_idle](#trap_obj_limit_mulan_idle) |
| 6 | 39 | [trap_skateboard_ride_edge](#trap_skateboard_ride_edge) |
| 6 | 40 | [trap_obj_limit_peterpan_idle](#trap_obj_limit_peterpan_idle) |
| 6 | 41 | [trap_skateboard_edge_jump](#trap_skateboard_edge_jump) |
| 6 | 42 | [trap_obj_hop_direct](#trap_obj_hop_direct) |
| 6 | 43 | [trap_command_limit_trinity_commbo_start](#trap_command_limit_trinity_commbo_start) |
| 6 | 44 | [trap_obj_limit_riku_idle](#trap_obj_limit_riku_idle) |
| 6 | 45 | [trap_obj_hide_shadow](#trap_obj_hide_shadow) |
| 6 | 46 | [trap_obj_rc_stop_all](#trap_obj_rc_stop_all) |
| 6 | 47 | [trap_obj_stop_end_all](#trap_obj_stop_end_all) |
| 6 | 48 | [trap_skateboardscore_add_count](#trap_skateboardscore_add_count) |
| 6 | 49 | [trap_obj_is_stop](#trap_obj_is_stop) |
| 6 | 50 | [trap_obj_stop_start](#trap_obj_stop_start) |
| 6 | 51 | [trap_bghit_check_line](#trap_bghit_check_line) |
| 6 | 52 | [trap_bghit_get_normal](#trap_bghit_get_normal) |
| 6 | 53 | [trap_bghit_is_hit](#trap_bghit_is_hit) |
| 6 | 54 | [trap_bghit_get_cross_pos](#trap_bghit_get_cross_pos) |
| 6 | 55 | [trap_bghit_get_kind](#trap_bghit_get_kind) |
| 6 | 56 | [trap_target_set_group](#trap_target_set_group) |
| 6 | 57 | [trap_target_get_group](#trap_target_get_group) |
| 6 | 58 | [trap_obj_act_child_push](#trap_obj_act_child_push) |
| 6 | 59 | [trap_xemnas_get_obj](#trap_xemnas_get_obj) |
| 6 | 60 | [trap_obj_set_stealth_color](#trap_obj_set_stealth_color) |
| 6 | 61 | [trap_obj_is_hook](#trap_obj_is_hook) |
| 6 | 62 | [trap_obj_carpet_obj_idle](#trap_obj_carpet_obj_idle) |
| 6 | 63 | [trap_obj_is_damage_motion](#trap_obj_is_damage_motion) |
| 6 | 64 | [trap_obj_show_shadow](#trap_obj_show_shadow) |
| 6 | 65 | [trap_obj_set_scissoring](#trap_obj_set_scissoring) |
| 6 | 66 | [trap_obj_clear_hitback](#trap_obj_clear_hitback) |
| 6 | 67 | [trap_obj_party_attack](#trap_obj_party_attack) |
| 6 | 68 | [trap_strike_raid_calc_xyzrot](#trap_strike_raid_calc_xyzrot) |
| 6 | 69 | [trap_larxene_dead](#trap_larxene_dead) |
| 6 | 70 | [trap_obj_play_se_loop](#trap_obj_play_se_loop) |
| 6 | 71 | [trap_obj_fadeout_se](#trap_obj_fadeout_se) |
| 7 | 0 | [trap_enemy_stop_all_start](#trap_enemy_stop_all_start) |
| 7 | 1 | [trap_enemy_stop_all_end](#trap_enemy_stop_all_end) |
| 7 | 2 | [trap_attack_hit_mark_pos](#trap_attack_hit_mark_pos) |
| 7 | 3 | [trap_flare_init](#trap_flare_init) |
| 7 | 4 | [trap_flare_new](#trap_flare_new) |
| 7 | 5 | [trap_flare_free](#trap_flare_free) |
| 7 | 6 | [trap_flare_set_pos](#trap_flare_set_pos) |
| 7 | 7 | [trap_flare_set_radius](#trap_flare_set_radius) |
| 7 | 8 | [trap_flare_set_effect](#trap_flare_set_effect) |
| 7 | 9 | [trap_flare_set_target](#trap_flare_set_target) |
| 7 | 10 | [trap_flare_get_pos](#trap_flare_get_pos) |
| 7 | 11 | [trap_flare_is_empty](#trap_flare_is_empty) |
| 7 | 12 | [trap_limit_aladdin_exclamation_mark_pos](#trap_limit_aladdin_exclamation_mark_pos) |
| 7 | 13 | [trap_magic_calc_speed](#trap_magic_calc_speed) |
| 7 | 14 | [trap_attack_set_reaction_offset](#trap_attack_set_reaction_offset) |
| 7 | 15 | [trap_friend_get_target_size](#trap_friend_get_target_size) |
| 7 | 16 | [trap_friend_get_current_action](#trap_friend_get_current_action) |
| 7 | 17 | [trap_friend_set_script_status](#trap_friend_set_script_status) |
| 7 | 18 | [trap_friend_get_main_status](#trap_friend_get_main_status) |
| 7 | 19 | [trap_friend_update_target](#trap_friend_update_target) |
| 7 | 21 | [trap_obj_limit_hover_set_spec](#trap_obj_limit_hover_set_spec) |
| 7 | 24 | [trap_friend_enable_system_wishdir](#trap_friend_enable_system_wishdir) |
| 7 | 25 | [trap_friend_disable_system_wishdir](#trap_friend_disable_system_wishdir) |
| 7 | 26 | [trap_friend_call](#trap_friend_call) |
| 7 | 27 | [trap_limit_start_command](#trap_limit_start_command) |
| 7 | 28 | [trap_trinity_shot_init](#trap_trinity_shot_init) |
| 7 | 29 | [trap_trinity_shot_start](#trap_trinity_shot_start) |
| 7 | 30 | [trap_trinity_shot_ensure](#trap_trinity_shot_ensure) |
| 7 | 31 | [trap_trinity_shot_set_effect_id](#trap_trinity_shot_set_effect_id) |
| 7 | 32 | [trap_vacuum_set_effective_range](#trap_vacuum_set_effective_range) |
| 7 | 33 | [trap_enemy_summon_entry](#trap_enemy_summon_entry) |
| 7 | 34 | [trap_attack_set_rc_owner](#trap_attack_set_rc_owner) |
| 7 | 35 | [trap_summon_is_exec](#trap_summon_is_exec) |
| 7 | 36 | [trap_limit_reset_hit_counter](#trap_limit_reset_hit_counter) |
| 8 | 0 | [trap_obj_target_radius](#trap_obj_target_radius) |
| 8 | 1 | [trap_player_push_ability_button](#trap_player_push_ability_button) |
| 8 | 2 | [trap_obj_set_xyzrot](#trap_obj_set_xyzrot) |
| 8 | 3 | [trap_special_last_xemnus_laser_start](#trap_special_last_xemnus_laser_start) |
| 8 | 4 | [trap_special_last_xemnus_laser_attack](#trap_special_last_xemnus_laser_attack) |
| 8 | 5 | [trap_special_last_xemnus_laser_end](#trap_special_last_xemnus_laser_end) |
| 8 | 6 | [trap_special_last_xemnus_laser_optimize](#trap_special_last_xemnus_laser_optimize) |
| 8 | 7 | [trap_special_last_xemnus_laser_optimize_end](#trap_special_last_xemnus_laser_optimize_end) |
| 8 | 8 | [trap_camera_apply_inverse_pos](#trap_camera_apply_inverse_pos) |
| 10 | 0 | [trap_empty_func](#trap_empty_func) |
| 10 | 1 | [trap_stitch_set_screen_position](#trap_stitch_set_screen_position) |
| 10 | 2 | [trap_stitch_get_screen_position](#trap_stitch_get_screen_position) |
| 10 | 3 | [trap_friend_start_limit](#trap_friend_start_limit) |
| 10 | 4 | [trap_friend_end_limit](#trap_friend_end_limit) |
| 10 | 5 | [trap_chickenlittle_get_shoot_target](#trap_chickenlittle_get_shoot_target) |
| 10 | 6 | [trap_obj_set_special_command](#trap_obj_set_special_command) |
| 10 | 7 | [trap_obj_reset_special_command](#trap_obj_reset_special_command) |
| 10 | 8 | [trap_friend_get_target_last_position](#trap_friend_get_target_last_position) |
| 10 | 9 | [trap_genie_change_form](#trap_genie_change_form) |
| 10 | 10 | [trap_genie_get_limit_command](#trap_genie_get_limit_command) |
| 10 | 11 | [trap_obj_set_stop_timer](#trap_obj_set_stop_timer) |
| 10 | 12 | [trap_stitch_effect_start](#trap_stitch_effect_start) |
| 10 | 13 | [trap_stitch_shot_effect](#trap_stitch_shot_effect) |
| 10 | 14 | [trap_friend_set_target](#trap_friend_set_target) |
| 10 | 15 | [trap_sysobj_motion_cont_push](#trap_sysobj_motion_cont_push) |
| 10 | 16 | [trap_stitch_effect_kill](#trap_stitch_effect_kill) |
| 10 | 17 | [trap_sysobj_is_zako](#trap_sysobj_is_zako) |
| 10 | 18 | [trap_sysobj_is_boss](#trap_sysobj_is_boss) |
| 10 | 19 | [trap_sysobj_is_limit](#trap_sysobj_is_limit) |
| 10 | 20 | [trap_friend_follow_player](#trap_friend_follow_player) |
| 10 | 21 | [trap_friend_follow_enemy](#trap_friend_follow_enemy) |
| 10 | 22 | [trap_sysobj_is_blow](#trap_sysobj_is_blow) |
| 10 | 23 | [trap_enemy_is_attacked_from](#trap_enemy_is_attacked_from) |
| 10 | 24 | [tarp_friend_is_equiped_ability](#tarp_friend_is_equiped_ability) |
| 10 | 25 | [trap_peterpan_receive_notify_player_target](#trap_peterpan_receive_notify_player_target) |
| 10 | 26 | [trap_peterpan_accept_notify_player_target](#trap_peterpan_accept_notify_player_target) |
| 10 | 27 | [trap_friend_enable_inertia](#trap_friend_enable_inertia) |
| 10 | 28 | [trap_friend_disable_inertia](#trap_friend_disable_inertia) |
| 10 | 29 | [trap_friend_use_item](#trap_friend_use_item) |
| 10 | 30 | [trap_sysobj_is_finish_blow](#trap_sysobj_is_finish_blow) |
| 10 | 31 | [trap_sysobj_is_summon](#trap_sysobj_is_summon) |
| 10 | 32 | [trap_stitch_move_request](#trap_stitch_move_request) |
| 10 | 33 | [trap_friend_get_player_attacker](#trap_friend_get_player_attacker) |
| 10 | 34 | [trap_friend_remove_player_attacker](#trap_friend_remove_player_attacker) |
| 10 | 35 | [trap_friend_get_action_param](#trap_friend_get_action_param) |
| 10 | 36 | [trap_friend_is_control](#trap_friend_is_control) |
| 10 | 37 | [trap_friend_is_moveonly](#trap_friend_is_moveonly) |
| 10 | 38 | [trap_attack_is_finish](#trap_attack_is_finish) |
| 10 | 39 | [trap_friend_action_clear](#trap_friend_action_clear) |
| 10 | 40 | [trap_obj_is_motion_sync](#trap_obj_is_motion_sync) |
| 10 | 41 | [trap_friend_start_leave](#trap_friend_start_leave) |
| 10 | 42 | [trap_friend_is_start_leave](#trap_friend_is_start_leave) |
| 10 | 43 | [trap_obj_set_use_mp](#trap_obj_set_use_mp) |
| 10 | 44 | [trap_obj_is_tornado](#trap_obj_is_tornado) |
| 10 | 45 | [trap_sheet_get_drive_time](#trap_sheet_get_drive_time) |
| 10 | 46 | [trap_friend_disable_follow_enemy](#trap_friend_disable_follow_enemy) |
| 10 | 47 | [trap_friend_enable_follow_enemy](#trap_friend_enable_follow_enemy) |
| 10 | 48 | [trap_friend_disable_follow_player](#trap_friend_disable_follow_player) |
| 10 | 49 | [trap_friend_enable_follow_player](#trap_friend_enable_follow_player) |
| 10 | 50 | [trap_sheet_get_mp](#trap_sheet_get_mp) |
| 10 | 51 | [trap_chickenlittle_get_nearest_target](#trap_chickenlittle_get_nearest_target) |
| 10 | 52 | [trap_btlobj_is_reflect_motion](#trap_btlobj_is_reflect_motion) |
| 10 | 53 | [trap_friend_add_watch_effect](#trap_friend_add_watch_effect) |
| 10 | 54 | [trap_friend_is_effect_exist](#trap_friend_is_effect_exist) |
| 10 | 55 | [trap_target_searcher_set_check_hide_from_friend](#trap_target_searcher_set_check_hide_from_friend) |
| 10 | 56 | [trap_friend_invalidate_warp_point](#trap_friend_invalidate_warp_point) |
| 10 | 57 | [trap_friend_add_warp_point](#trap_friend_add_warp_point) |
| 10 | 58 | [trap_friend_link_magic](#trap_friend_link_magic) |
| 10 | 59 | [trap_chickenlittle_set_shoot_target](#trap_chickenlittle_set_shoot_target) |

## Instrument list


### pushImm

_Format:_

`pushImm  imm32`

_Description:_


> push(_imm32_);





_Example:_

> pushImm -123
> pushImm 123
> push -2147483648
> push 2147483647



_Operations:_


```
push(full_ext:4);

```



### pushImm

_Format:_

`pushImm  imm32`

_Description:_


> push(_imm32_);





_Example:_

> pushImm -123
> pushImm 123
> push -2147483648
> push 2147483647



_Operations:_


```
push(full_ext:4);

```



### pushFromPSp

_Format:_

`pushFromPSp  imm16`

_Description:_


> push(sp + _imm16_)





_Example:_

> pushFromPSp -1



_Operations:_


> Not yet operated.



### pushFromPWp

_Format:_

`pushFromPWp  imm16`

_Description:_


> push(wp + _imm16_)





_Operations:_


> Not yet operated.



### pushFromPSpVal

_Format:_

`pushFromPSpVal  imm16`

_Description:_


> push(fetch(sp) + _imm16_)





_Operations:_


> Not yet operated.



### pushFromPAi

_Format:_

`pushFromPAi  imm16`

_Description:_


> push(ai + 16 + 2 * _imm16_)





_Operations:_


> Not yet operated.



### pushFromFSp

_Format:_

`pushFromFSp  imm16`

_Description:_


> push(fetch(sp + _imm16_))





_Operations:_


> Not yet operated.



### pushFromFWp

_Format:_

`pushFromFWp  imm16`

_Description:_


> push(fetch(wp + _imm16_))





_Operations:_


> Not yet operated.



### pushFromFSpVal

_Format:_

`pushFromFSpVal  imm16`

_Description:_


> push(fetch(fetch(sp) + _imm16_))





_Operations:_


> Not yet operated.



### pushFromFAi

_Format:_

`pushFromFAi  imm16`

_Description:_


> push(fetch(ai + 16 + 2 * imm16));





_Operations:_


> Not yet operated.



### popToSp

_Format:_

`popToSp  imm16`

_Description:_


> store(sp + _imm16_, pop())





_Operations:_


> Not yet operated.



### popToWp

_Format:_

`popToWp  imm16`

_Description:_


> store(wp + _imm16_, pop())





_Operations:_


> Not yet operated.



### popToSpVal

_Format:_

`popToSpVal  imm16`

_Description:_


> store(fetch(sp) + _imm16_, pop())





_Operations:_


> Not yet operated.



### popToAi

_Format:_

`popToAi  imm16`

_Description:_


> store(ai + 16 + 2 * _imm16_, pop())





_Operations:_


> Not yet operated.



### memcpyToSp

_Format:_

`memcpyToSp  imm16,imm16_2`

_Description:_


> memcpy(sp + _imm16_2_, pop(), _imm16_);





_Operations:_


> Not yet operated.



### memcpyToWp

_Format:_

`memcpyToWp  imm16,imm16_2`

_Description:_


> memcpy(wp + _imm16_2_, pop(), _imm16_);





_Operations:_


> Not yet operated.



### memcpyToSpVal

_Format:_

`memcpyToSpVal  imm16,imm16_2`

_Description:_


> memcpy(fetch(sp) + _imm16_2_, pop(), _imm16_);





_Operations:_


> Not yet operated.



### memcpyToSpAi

_Format:_

`memcpyToSpAi  imm16,imm16_2`

_Description:_


> memcpy(ai + 16 + _imm16_2_, pop(), _imm16_);





_Operations:_


> Not yet operated.



### fetchValue

_Format:_

`fetchValue  imm16`

_Description:_


> push(fetch(pop() + _imm16_))





_Operations:_


> Not yet operated.



### memcpy

_Format:_

`memcpy  ssub`

_Description:_


> src = pop(); dst = pop(); memcpy(dst, src, ssub);

Copy single word (4 bytes), if ssub == 0.





_Operations:_


> Not yet operated.



### cfti

_Format:_

`cfti  `

_Description:_


> push(popf())

Retrieves the last value pushed on to the stack and converts it from a signed integer to a floating point value, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
tmp = round(tmp);
push(tmp);

```



### neg

_Format:_

`neg  `

_Description:_


> push(-pop())

Retrieves the last value pushed on to the stack and converts it to a negative number, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
tmp=-tmp;
push(tmp);

```



### inv

_Format:_

`inv  `

_Description:_


> push(~pop())

Retrieves the last value pushed on to the stack and inverts it, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
tmp = ~tmp;
push(tmp);

```



### eqz

_Format:_

`eqz  `

_Description:_


> push(pop() == 0)

Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
local ret = (tmp == 0);
push(ret);

```



### abs

_Format:_

`abs  `

_Description:_


> push(abs(pop()))

Retrieves the last value pushed on to the stack and converts it to an absolute value, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
if(tmp s<= 0) goto <min>;
goto <done>;
<min>
    tmp=-tmp;     
<done>
    push(tmp);

```



### msb

_Format:_

`msb  `

_Description:_


> push(srl(pop(), 31))

Retrieves the last value pushed on to the stack and gets back its most significant bit, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
tmp = tmp >> 0x1F;
push(tmp);

```



### info

_Format:_

`info  `

_Description:_


> push(slti(pop(), 1))

Retrieves the last value pushed on to the stack and compares it to one, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
push((tmp s< 1));

```



### eqz

_Format:_

`eqz  `

_Description:_


> push(pop() == 0)

Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
local ret = (tmp == 0);
push(ret);

```



### neqz

_Format:_

`neqz  `

_Description:_


> push(pop() != 0)

Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
push((tmp != 0));

```



### msbi

_Format:_

`msbi  `

_Description:_


> push(srl(nor(0, pop()), 31))

Retrieves the last value pushed on to the stack and gets back its most significant bit and inverts it, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
tmp = tmp >> 0x1F;
push(~tmp);

```



### ipos

_Format:_

`ipos  `

_Description:_


> push(slt(0, pop()))

Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
push((tmp s> 0));

```



### citf

_Format:_

`citf  `

_Description:_


Retrieves the last value pushed on to the stack and converts it from a signed integer to a floating point value, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
tmp=int2float(tmp);
push(tmp);

```



### negf

_Format:_

`negf  `

_Description:_


Retrieves the last value pushed on to the stack and converts it to a negative value, pushing back the result to the stack.





_Operations:_


> Not yet operated.



### absf

_Format:_

`absf  `

_Description:_


Retrieves the last value pushed on to the stack and converts it to an absolute value, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
tmp=abs(tmp);
push(tmp);

```



### infzf

_Format:_

`infzf  `

_Description:_


Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
push((tmp f< 0));

```



### infoezf

_Format:_

`infoezf  `

_Description:_


Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
push((tmp f<= 0));

```



### eqzf

_Format:_

`eqzf  `

_Description:_


Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
push((tmp f== 0));

```



### neqzf

_Format:_

`neqzf  `

_Description:_


Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
push((tmp f!= 0));

```



### supoezf

_Format:_

`supoezf  `

_Description:_


Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
push((tmp f>= 0));

```



### supzf

_Format:_

`supzf  `

_Description:_


Retrieves the last value pushed on to the stack and compares it to zero, pushing back the result to the stack.





_Operations:_


```
local tmp:4 = sp;
pop(tmp);
push((tmp f> 0));

```



### add

_Format:_

`add  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### sub

_Format:_

`sub  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### mul

_Format:_

`mul  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### div

_Format:_

`div  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### mod

_Format:_

`mod  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### and

_Format:_

`and  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### or

_Format:_

`or  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### xor

_Format:_

`xor  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### sll

_Format:_

`sll  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### sra

_Format:_

`sra  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### eqzv

_Format:_

`eqzv  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### neqzv

_Format:_

`neqzv  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### addf

_Format:_

`addf  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### subf

_Format:_

`subf  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### mulf

_Format:_

`mulf  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### divf

_Format:_

`divf  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### modf

_Format:_

`modf  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### jmp

_Format:_

`jmp  imm16`

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### jnz

_Format:_

`jnz  imm16`

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### jz

_Format:_

`jz  imm16`

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### gosub

_Format:_

`gosub  ssub,imm16`

_Description:_


> sp += ssub
>
> gosub(_imm16_)





_Operations:_


> Not yet operated.



### halt

_Format:_

`halt  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### exit

_Format:_

`exit  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### ret

_Format:_

`ret  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### drop

_Format:_

`drop  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### dup

_Format:_

`dup  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### sin

_Format:_

`sin  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### cos

_Format:_

`cos  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### degr

_Format:_

`degr  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### radd

_Format:_

`radd  `

_Description:_


> Not yet described.




_Operations:_


> Not yet operated.



### syscall

_Format:_

`syscall  ssub,imm16`

_Description:_


Notes:

- tableIdx = _ssub_
- funcIdx = _imm16_

> syscall(_ssub_, _imm16_)





_Operations:_


> Not yet operated.



### gosub32

_Format:_

`gosub32  ssub,imm32`

_Description:_


> sp += ssub
>
> gosub(_imm32_)





_Operations:_


> Not yet operated.




## Syscall list


### trap_puti

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 0 ; trap_puti (2 in, 0 out)

```






### trap_putf

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 1 ; trap_putf (2 in, 0 out)

```






### trap_puts

_Format:_

```
push unk1 ; unknown
syscall 0, 2 ; trap_puts (1 in, 0 out)

```






### trap_frametime

_Format:_

```
syscall 0, 3 ; trap_frametime (0 in, 1 out)
pop unk ; unknown
```






### trap_vector_add

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 4 ; trap_vector_add (2 in, 1 out)
pop unk ; unknown
```






### trap_vector_sub

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 5 ; trap_vector_sub (2 in, 1 out)
pop unk ; unknown
```






### trap_vector_len

_Format:_

```
push unk1 ; unknown
syscall 0, 6 ; trap_vector_len (1 in, 1 out)
pop unk ; unknown
```






### trap_vector_normalize

_Format:_

```
push unk1 ; unknown
syscall 0, 7 ; trap_vector_normalize (1 in, 1 out)
pop unk ; unknown
```






### trap_vector_dump

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 8 ; trap_vector_dump (2 in, 0 out)

```






### trap_thread_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 0, 9 ; trap_thread_start (4 in, 1 out)
pop unk ; unknown
```






### trap_file_is_reading

_Format:_

```
syscall 0, 11 ; trap_file_is_reading (0 in, 1 out)
pop unk ; unknown
```






### trap_file_flush

_Format:_

```
syscall 0, 12 ; trap_file_flush (0 in, 0 out)

```






### trap_vector_roty

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 13 ; trap_vector_roty (2 in, 1 out)
pop unk ; unknown
```






### trap_progress_set_flag

_Format:_

```
push unk1 ; unknown
syscall 0, 14 ; trap_progress_set_flag (1 in, 0 out)

```






### trap_progress_check_flag

_Format:_

```
push unk1 ; unknown
syscall 0, 15 ; trap_progress_check_flag (1 in, 1 out)
pop unk ; unknown
```






### trap_random_get

_Format:_

```
push unk1 ; unknown
syscall 0, 16 ; trap_random_get (1 in, 1 out)
pop unk ; unknown
```






### trap_random_getf

_Format:_

```
push unk1 ; unknown
syscall 0, 17 ; trap_random_getf (1 in, 1 out)
pop unk ; unknown
```






### trap_random_range

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 18 ; trap_random_range (2 in, 1 out)
pop unk ; unknown
```






### trap_worldflag_set

_Format:_

```
push unk1 ; unknown
syscall 0, 19 ; trap_worldflag_set (1 in, 0 out)

```






### trap_worldflag_check

_Format:_

```
push unk1 ; unknown
syscall 0, 20 ; trap_worldflag_check (1 in, 1 out)
pop unk ; unknown
```






### trap_vector_get_rot_xz

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 21 ; trap_vector_get_rot_xz (2 in, 1 out)
pop unk ; unknown
```






### trap_abs

_Format:_

```
push unk1 ; unknown
syscall 0, 22 ; trap_abs (1 in, 1 out)
pop unk ; unknown
```






### trap_absf

_Format:_

```
push unk1 ; unknown
syscall 0, 23 ; trap_absf (1 in, 1 out)
pop unk ; unknown
```






### trap_stputi

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 24 ; trap_stputi (2 in, 0 out)

```






### trap_stputf

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 25 ; trap_stputf (2 in, 0 out)

```






### trap_stputs

_Format:_

```
push unk1 ; unknown
syscall 0, 26 ; trap_stputs (1 in, 0 out)

```






### func_system_set_game_speed

_Format:_

```
push unk1 ; unknown
syscall 0, 27 ; func_system_set_game_speed (1 in, 0 out)

```






### method_blur_init

_Format:_

```
push unk1 ; unknown
syscall 0, 28 ; method_blur_init (1 in, 0 out)

```






### method_blur_start

_Format:_

```
push unk1 ; unknown
syscall 0, 29 ; method_blur_start (1 in, 0 out)

```






### method_blur_stop

_Format:_

```
push unk1 ; unknown
syscall 0, 30 ; method_blur_stop (1 in, 0 out)

```






### func_screen_whiteout

_Format:_

```
push unk1 ; unknown
syscall 0, 31 ; func_screen_whiteout (1 in, 0 out)

```






### func_screen_whitein

_Format:_

```
push unk1 ; unknown
syscall 0, 32 ; func_screen_whitein (1 in, 0 out)

```






### method_vector_scale

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 35 ; method_vector_scale (2 in, 0 out)

```






### trap_vector_mul

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 36 ; trap_vector_mul (2 in, 1 out)
pop unk ; unknown
```






### trap_vector_div

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 37 ; trap_vector_div (2 in, 1 out)
pop unk ; unknown
```






### trap_effect_set_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 38 ; trap_effect_set_pos (2 in, 0 out)

```






### trap_effect_set_scale

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 39 ; trap_effect_set_scale (2 in, 0 out)

```






### trap_effect_set_rot

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 40 ; trap_effect_set_rot (2 in, 0 out)

```






### trap_effect_set_dir

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 41 ; trap_effect_set_dir (2 in, 0 out)

```






### trap_vector_atan_xz

_Format:_

```
push unk1 ; unknown
syscall 0, 42 ; trap_vector_atan_xz (1 in, 1 out)
pop unk ; unknown
```






### trap_fixrad

_Format:_

```
push unk1 ; unknown
syscall 0, 43 ; trap_fixrad (1 in, 1 out)
pop unk ; unknown
```






### trap_effect_loop_end

_Format:_

```
push unk1 ; unknown
syscall 0, 44 ; trap_effect_loop_end (1 in, 0 out)

```






### trap_vector_addf

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 0, 45 ; trap_vector_addf (3 in, 0 out)

```






### trap_vector_homing

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 0, 46 ; trap_vector_homing (3 in, 0 out)

```






### trap_memory_alloc

_Format:_

```
push unk1 ; unknown
syscall 0, 47 ; trap_memory_alloc (1 in, 1 out)
pop unk ; unknown
```






### trap_memory_free

_Format:_

```
push unk1 ; unknown
syscall 0, 48 ; trap_memory_free (1 in, 0 out)

```






### trap_effect_is_alive

_Format:_

```
push unk1 ; unknown
syscall 0, 49 ; trap_effect_is_alive (1 in, 1 out)
pop unk ; unknown
```






### trap_effect_is_active

_Format:_

```
push unk1 ; unknown
syscall 0, 50 ; trap_effect_is_active (1 in, 1 out)
pop unk ; unknown
```






### trap_effect_kill

_Format:_

```
push unk1 ; unknown
syscall 0, 51 ; trap_effect_kill (1 in, 0 out)

```






### trap_effect_fadeout

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 0, 52 ; trap_effect_fadeout (3 in, 0 out)

```






### trap_effect_pos

_Format:_

```
push unk1 ; unknown
syscall 0, 53 ; trap_effect_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_effect_dir

_Format:_

```
push unk1 ; unknown
syscall 0, 54 ; trap_effect_dir (1 in, 1 out)
pop unk ; unknown
```






### trap_timer_count_down

_Format:_

```
push unk1 ; unknown
syscall 0, 55 ; trap_timer_count_down (1 in, 0 out)

```






### trap_timer_count_up

_Format:_

```
push unk1 ; unknown
syscall 0, 56 ; trap_timer_count_up (1 in, 0 out)

```






### trap_saveflag_set

_Format:_

```
push unk1 ; unknown
syscall 0, 57 ; trap_saveflag_set (1 in, 0 out)

```






### trap_saveflag_reset

_Format:_

```
push unk1 ; unknown
syscall 0, 58 ; trap_saveflag_reset (1 in, 0 out)

```






### trap_saveflag_check

_Format:_

```
push unk1 ; unknown
syscall 0, 59 ; trap_saveflag_check (1 in, 1 out)
pop unk ; unknown
```






### trap_assert

_Format:_

```
push unk1 ; unknown
syscall 0, 60 ; trap_assert (1 in, 0 out)

```






### trap_saveram_get_partram

_Format:_

```
push unk1 ; unknown
syscall 0, 61 ; trap_saveram_get_partram (1 in, 1 out)
pop unk ; unknown
```






### trap_partram_set_item_max

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 62 ; trap_partram_set_item_max (2 in, 0 out)

```






### trap_item_get

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 63 ; trap_item_get (2 in, 1 out)
pop unk ; unknown
```






### trap_sound_disable

_Format:_

```
syscall 0, 64 ; trap_sound_disable (0 in, 0 out)

```






### trap_sound_play_system

_Format:_

```
push unk1 ; unknown
syscall 0, 65 ; trap_sound_play_system (1 in, 0 out)

```






### trap_effect_pause

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 66 ; trap_effect_pause (2 in, 0 out)

```






### trap_effect_set_color

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 67 ; trap_effect_set_color (2 in, 0 out)

```






### trap_vector_rotx

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 68 ; trap_vector_rotx (2 in, 1 out)
pop unk ; unknown
```






### trap_menuflag_set

_Format:_

```
push unk1 ; unknown
syscall 0, 69 ; trap_menuflag_set (1 in, 0 out)

```






### trap_progress_is_second

_Format:_

```
syscall 0, 70 ; trap_progress_is_second (0 in, 1 out)
pop unk ; unknown
```






### trap_menuflag_reset

_Format:_

```
push unk1 ; unknown
syscall 0, 73 ; trap_menuflag_reset (1 in, 0 out)

```






### trap_screen_show_picture

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 74 ; trap_screen_show_picture (2 in, 0 out)

```






### trap_saveram_set_weapon

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 0, 75 ; trap_saveram_set_weapon (3 in, 0 out)

```






### trap_saveram_set_form_weapon

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 76 ; trap_saveram_set_form_weapon (2 in, 0 out)

```






### trap_screen_cross_fade

_Format:_

```
push unk1 ; unknown
syscall 0, 77 ; trap_screen_cross_fade (1 in, 0 out)

```






### trap_vector_inter

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 0, 78 ; trap_vector_inter (3 in, 1 out)
pop unk ; unknown
```






### trap_effect_add_dead_block

_Format:_

```
push unk1 ; unknown
syscall 0, 79 ; trap_effect_add_dead_block (1 in, 0 out)

```






### trap_pad_is_button

_Format:_

```
push unk1 ; unknown
syscall 0, 80 ; trap_pad_is_button (1 in, 1 out)
pop unk ; unknown
```






### trap_pad_is_trigger

_Format:_

```
push unk1 ; unknown
syscall 0, 81 ; trap_pad_is_trigger (1 in, 1 out)
pop unk ; unknown
```






### trap_vector_outer_product

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 82 ; trap_vector_outer_product (2 in, 1 out)
pop unk ; unknown
```






### trap_vector_rot

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 0, 83 ; trap_vector_rot (3 in, 1 out)
pop unk ; unknown
```






### trap_vector_angle

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 84 ; trap_vector_angle (2 in, 1 out)
pop unk ; unknown
```






### trap_effect_loop_end_kill

_Format:_

```
push unk1 ; unknown
syscall 0, 85 ; trap_effect_loop_end_kill (1 in, 0 out)

```






### trap_effect_set_type

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 86 ; trap_effect_set_type (2 in, 0 out)

```






### trap_screen_fadeout

_Format:_

```
push unk1 ; unknown
syscall 0, 87 ; trap_screen_fadeout (1 in, 0 out)

```






### trap_screen_fadein

_Format:_

```
push unk1 ; unknown
syscall 0, 88 ; trap_screen_fadein (1 in, 0 out)

```






### trap_menuflag_check

_Format:_

```
push unk1 ; unknown
syscall 0, 89 ; trap_menuflag_check (1 in, 1 out)
pop unk ; unknown
```






### trap_vector_draw

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 0, 90 ; trap_vector_draw (5 in, 0 out)

```






### trap_vector_inner_prodcut

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 91 ; trap_vector_inner_prodcut (2 in, 1 out)
pop unk ; unknown
```






### trap_partram_add_attack

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 92 ; trap_partram_add_attack (2 in, 0 out)

```






### trap_partram_add_wisdom

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 93 ; trap_partram_add_wisdom (2 in, 0 out)

```






### trap_partram_add_defence

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 94 ; trap_partram_add_defence (2 in, 0 out)

```






### trap_partram_set_levelup_type

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 95 ; trap_partram_set_levelup_type (2 in, 0 out)

```






### trap_partram_add_ap

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 96 ; trap_partram_add_ap (2 in, 0 out)

```






### trap_item_reduce

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 97 ; trap_item_reduce (2 in, 0 out)

```






### trap_saveram_set_form_ability

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 0, 98 ; trap_saveram_set_form_ability (2 in, 0 out)

```






### trap_partram_add_ability

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 0, 99 ; trap_partram_add_ability (3 in, 0 out)

```






### trap_saveram_increment_friend_recov

_Format:_

```
syscall 0, 100 ; trap_saveram_increment_friend_recov (0 in, 0 out)

```






### trap_progress_is_secret_movie

_Format:_

```
syscall 0, 101 ; trap_progress_is_secret_movie (0 in, 1 out)
pop unk ; unknown
```






### trap_vector_to_angle

_Format:_

```
push unk1 ; unknown
syscall 0, 102 ; trap_vector_to_angle (1 in, 1 out)
pop unk ; unknown
```






### trap_progress_is_fm_secret_movie

_Format:_

```
syscall 0, 103 ; trap_progress_is_fm_secret_movie (0 in, 1 out)
pop unk ; unknown
```






### trap_sound_set_bgse_volume

_Format:_

```
push unk1 ; unknown
syscall 0, 104 ; trap_sound_set_bgse_volume (1 in, 0 out)

```






### trap_sysobj_appear

_Format:_

```
push unk1 ; unknown
syscall 1, 0 ; trap_sysobj_appear (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_rot

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 1 ; trap_obj_set_rot (2 in, 0 out)

```






### trap_sysobj_moveto

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 2 ; trap_sysobj_moveto (3 in, 1 out)
pop unk ; unknown
```






### trap_sysobj_player

_Format:_

```
syscall 1, 3 ; trap_sysobj_player (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_wish_dir

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 4 ; trap_obj_wish_dir (2 in, 0 out)

```






### trap_act_table_init

_Format:_

```
push unk1 ; unknown
syscall 1, 5 ; trap_act_table_init (1 in, 0 out)

```






### trap_act_table_add

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
push unk6 ; unknown
push unk7 ; unknown
push unk8 ; unknown
push unk9 ; unknown
push unk10 ; unknown
push unk11 ; unknown
push unk12 ; unknown
syscall 1, 6 ; trap_act_table_add (12 in, 0 out)

```






### trap_obj_set_act_table

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 7 ; trap_obj_set_act_table (2 in, 0 out)

```






### trap_obj_act_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 8 ; trap_obj_act_start (2 in, 0 out)

```






### trap_obj_act_push

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 9 ; trap_obj_act_push (2 in, 0 out)

```






### trap_obj_is_act_exec

_Format:_

```
push unk1 ; unknown
syscall 1, 10 ; trap_obj_is_act_exec (1 in, 1 out)
pop unk ; unknown
```






### trap_sysobj_motion_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 11 ; trap_sysobj_motion_start (3 in, 0 out)

```






### trap_sysobj_motion_change

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 12 ; trap_sysobj_motion_change (3 in, 0 out)

```






### trap_sysobj_motion_push

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 13 ; trap_sysobj_motion_push (3 in, 0 out)

```






### trap_sysobj_motion_is_end

_Format:_

```
push unk1 ; unknown
syscall 1, 14 ; trap_sysobj_motion_is_end (1 in, 1 out)
pop unk ; unknown
```






### trap_sysobj_motion_id

_Format:_

```
push unk1 ; unknown
syscall 1, 15 ; trap_sysobj_motion_id (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_leave_force

_Format:_

```
push unk1 ; unknown
syscall 1, 17 ; trap_obj_leave_force (1 in, 0 out)

```






### trap_obj_attach

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
push unk6 ; unknown
syscall 1, 18 ; trap_obj_attach (6 in, 0 out)

```






### trap_sysobj_fadeout

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 19 ; trap_sysobj_fadeout (2 in, 0 out)

```






### trap_sysobj_fadein

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 20 ; trap_sysobj_fadein (2 in, 0 out)

```






### trap_obj_effect_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 21 ; trap_obj_effect_start (4 in, 1 out)
pop unk ; unknown
```






### trap_obj_effect_start_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 22 ; trap_obj_effect_start_pos (5 in, 1 out)
pop unk ; unknown
```






### trap_area_world

_Format:_

```
syscall 1, 23 ; trap_area_world (0 in, 1 out)
pop unk ; unknown
```






### trap_area_area

_Format:_

```
syscall 1, 24 ; trap_area_area (0 in, 1 out)
pop unk ; unknown
```






### trap_area_map_set

_Format:_

```
syscall 1, 25 ; trap_area_map_set (0 in, 1 out)
pop unk ; unknown
```






### trap_area_battle_set

_Format:_

```
syscall 1, 26 ; trap_area_battle_set (0 in, 1 out)
pop unk ; unknown
```






### trap_area_event_set

_Format:_

```
syscall 1, 27 ; trap_area_event_set (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_leave

_Format:_

```
push unk1 ; unknown
syscall 1, 28 ; trap_obj_leave (1 in, 0 out)

```






### trap_obj_motion_capture

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 29 ; trap_obj_motion_capture (4 in, 1 out)
pop unk ; unknown
```






### trap_area_jump

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 30 ; trap_area_jump (3 in, 0 out)

```






### trap_area_setjump

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 31 ; trap_area_setjump (2 in, 0 out)

```






### trap_message_open

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 32 ; trap_message_open (2 in, 1 out)
pop unk ; unknown
```






### trap_message_close

_Format:_

```
push unk1 ; unknown
syscall 1, 33 ; trap_message_close (1 in, 0 out)

```






### trap_event_is_exec

_Format:_

```
syscall 1, 34 ; trap_event_is_exec (0 in, 1 out)
pop unk ; unknown
```






### trap_area_init

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 35 ; trap_area_init (3 in, 0 out)

```






### trap_bg_hide

_Format:_

```
push unk1 ; unknown
syscall 1, 36 ; trap_bg_hide (1 in, 0 out)

```






### trap_bg_show

_Format:_

```
push unk1 ; unknown
syscall 1, 37 ; trap_bg_show (1 in, 0 out)

```






### trap_obj_set_team

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 38 ; trap_obj_set_team (2 in, 0 out)

```






### trap_obj_unit_arg

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 39 ; trap_obj_unit_arg (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_is_pirate_shade

_Format:_

```
push unk1 ; unknown
syscall 1, 40 ; trap_obj_is_pirate_shade (1 in, 1 out)
pop unk ; unknown
```






### trap_signal_call

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 41 ; trap_signal_call (2 in, 0 out)

```






### func_obj_control_off

_Format:_

```
push unk1 ; unknown
syscall 1, 42 ; func_obj_control_off (1 in, 0 out)

```






### func_obj_control_on

_Format:_

```
push unk1 ; unknown
syscall 1, 43 ; func_obj_control_on (1 in, 0 out)

```






### func_history_clear_enemy

_Format:_

```
syscall 1, 44 ; func_history_clear_enemy (0 in, 0 out)

```






### func_area_activate_unit

_Format:_

```
push unk1 ; unknown
syscall 1, 45 ; func_area_activate_unit (1 in, 0 out)

```






### func_bg_barrier_on

_Format:_

```
syscall 1, 46 ; func_bg_barrier_on (0 in, 0 out)

```






### func_bg_barrier_off

_Format:_

```
syscall 1, 47 ; func_bg_barrier_off (0 in, 0 out)

```






### method_message_is_end

_Format:_

```
push unk1 ; unknown
syscall 1, 48 ; method_message_is_end (1 in, 1 out)
pop unk ; unknown
```






### method_obj_enable_reaction_command

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 49 ; method_obj_enable_reaction_command (3 in, 0 out)

```






### method_obj_disable_reaction_command

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 50 ; method_obj_disable_reaction_command (3 in, 0 out)

```






### method_obj_reset_reaction_command

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 51 ; method_obj_reset_reaction_command (3 in, 0 out)

```






### method_obj_enable_collision

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 52 ; method_obj_enable_collision (2 in, 0 out)

```






### method_obj_disable_collision

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 53 ; method_obj_disable_collision (2 in, 0 out)

```






### method_obj_reset_collision

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 54 ; method_obj_reset_collision (2 in, 0 out)

```






### method_obj_jump

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 55 ; method_obj_jump (5 in, 0 out)

```






### method_obj_is_culling

_Format:_

```
push unk1 ; unknown
syscall 1, 56 ; method_obj_is_culling (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_is_jump

_Format:_

```
push unk1 ; unknown
syscall 1, 57 ; trap_obj_is_jump (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_fly

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 58 ; trap_obj_fly (3 in, 0 out)

```






### trap_obj_is_fly

_Format:_

```
push unk1 ; unknown
syscall 1, 59 ; trap_obj_is_fly (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_is_air

_Format:_

```
push unk1 ; unknown
syscall 1, 60 ; trap_obj_is_air (1 in, 1 out)
pop unk ; unknown
```






### trap_sysobj_motion_frame_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 61 ; trap_sysobj_motion_frame_start (4 in, 0 out)

```






### trap_obj_get_moved

_Format:_

```
push unk1 ; unknown
syscall 1, 62 ; trap_obj_get_moved (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_is_motion_in_loop

_Format:_

```
push unk1 ; unknown
syscall 1, 63 ; trap_obj_is_motion_in_loop (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_get_wish_movement

_Format:_

```
push unk1 ; unknown
syscall 1, 64 ; trap_obj_get_wish_movement (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_exec_fall

_Format:_

```
push unk1 ; unknown
syscall 1, 65 ; trap_obj_exec_fall (1 in, 0 out)

```






### trap_obj_exec_land

_Format:_

```
push unk1 ; unknown
syscall 1, 66 ; trap_obj_exec_land (1 in, 0 out)

```






### trap_obj_motion_get_length

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 67 ; trap_obj_motion_get_length (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_motion_get_loop_top

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 68 ; trap_obj_motion_get_loop_top (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_motion_get_time

_Format:_

```
push unk1 ; unknown
syscall 1, 69 ; trap_obj_motion_get_time (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_flag

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 70 ; trap_obj_set_flag (2 in, 0 out)

```






### trap_obj_reset_flag

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 71 ; trap_obj_reset_flag (2 in, 0 out)

```






### trap_obj_check_flag

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 72 ; trap_obj_check_flag (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_hover

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 73 ; trap_obj_hover (3 in, 0 out)

```






### trap_obj_idle

_Format:_

```
push unk1 ; unknown
syscall 1, 74 ; trap_obj_idle (1 in, 0 out)

```






### trap_obj_motion_hook

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 75 ; trap_obj_motion_hook (2 in, 0 out)

```






### trap_obj_motion_unhook

_Format:_

```
push unk1 ; unknown
syscall 1, 76 ; trap_obj_motion_unhook (1 in, 0 out)

```






### trap_obj_motion_is_hook

_Format:_

```
push unk1 ; unknown
syscall 1, 77 ; trap_obj_motion_is_hook (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_motion_is_no_control

_Format:_

```
push unk1 ; unknown
syscall 1, 78 ; trap_obj_motion_is_no_control (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_dir

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 79 ; trap_obj_set_dir (2 in, 0 out)

```






### trap_obj_turn_dir

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 80 ; trap_obj_turn_dir (3 in, 1 out)
pop unk ; unknown
```






### trap_obj_act_wedge

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 81 ; trap_obj_act_wedge (2 in, 0 out)

```






### trap_obj_thread_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 82 ; trap_obj_thread_start (5 in, 1 out)
pop unk ; unknown
```






### trap_obj_apply_bone_matrix

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 83 ; trap_obj_apply_bone_matrix (3 in, 1 out)
pop unk ; unknown
```






### trap_obj_sheet

_Format:_

```
push unk1 ; unknown
syscall 1, 84 ; trap_obj_sheet (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_texanm_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 85 ; trap_obj_texanm_start (2 in, 0 out)

```






### trap_obj_texanm_stop

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 86 ; trap_obj_texanm_stop (2 in, 0 out)

```






### trap_obj_effect_start_bind

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 87 ; trap_obj_effect_start_bind (4 in, 1 out)
pop unk ; unknown
```






### trap_obj_target_pos

_Format:_

```
push unk1 ; unknown
syscall 1, 88 ; trap_obj_target_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_move_request

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 89 ; trap_obj_move_request (3 in, 0 out)

```






### trap_obj_act_shout

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 90 ; trap_obj_act_shout (3 in, 0 out)

```






### trap_obj_star

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 91 ; trap_obj_star (2 in, 0 out)

```






### trap_obj_scatter_prize

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 92 ; trap_obj_scatter_prize (2 in, 0 out)

```






### trap_sysobj_party

_Format:_

```
push unk1 ; unknown
syscall 1, 93 ; trap_sysobj_party (1 in, 1 out)
pop unk ; unknown
```






### trap_sysobj_is_exist

_Format:_

```
push unk1 ; unknown
syscall 1, 94 ; trap_sysobj_is_exist (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_fly_to_jump

_Format:_

```
push unk1 ; unknown
syscall 1, 95 ; trap_obj_fly_to_jump (1 in, 0 out)

```






### trap_obj_get_action

_Format:_

```
push unk1 ; unknown
syscall 1, 96 ; trap_obj_get_action (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_spec

_Format:_

```
push unk1 ; unknown
syscall 1, 97 ; trap_obj_spec (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_step_pos

_Format:_

```
push unk1 ; unknown
syscall 1, 98 ; trap_obj_step_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_float_height

_Format:_

```
push unk1 ; unknown
syscall 1, 99 ; trap_obj_float_height (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_jump_height_to_uptime

_Format:_

```
push unk1 ; unknown
syscall 1, 100 ; trap_obj_jump_height_to_uptime (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_motion_is_capture

_Format:_

```
push unk1 ; unknown
syscall 1, 101 ; trap_obj_motion_is_capture (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_detach

_Format:_

```
push unk1 ; unknown
syscall 1, 102 ; trap_obj_detach (1 in, 0 out)

```






### trap_obj_set_detach_callback

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 103 ; trap_obj_set_detach_callback (3 in, 0 out)

```






### trap_obj_shadow_move_start

_Format:_

```
push unk1 ; unknown
syscall 1, 104 ; trap_obj_shadow_move_start (1 in, 0 out)

```






### trap_obj_shadow_move_end

_Format:_

```
push unk1 ; unknown
syscall 1, 105 ; trap_obj_shadow_move_end (1 in, 0 out)

```






### trap_signal_reserve_hp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 106 ; trap_signal_reserve_hp (4 in, 0 out)

```






### trap_obj_motion_speed

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 107 ; trap_obj_motion_speed (2 in, 0 out)

```






### trap_obj_show_part

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 108 ; trap_obj_show_part (2 in, 0 out)

```






### trap_obj_hide_part

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 109 ; trap_obj_hide_part (2 in, 0 out)

```






### trap_obj_get_appear_way

_Format:_

```
push unk1 ; unknown
syscall 1, 110 ; trap_obj_get_appear_way (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_movement

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 111 ; trap_obj_set_movement (3 in, 0 out)

```






### trap_obj_hook

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 112 ; trap_obj_hook (3 in, 0 out)

```






### trap_player_get_movement

_Format:_

```
push unk1 ; unknown
syscall 1, 113 ; trap_player_get_movement (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_search_by_entry

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 114 ; trap_obj_search_by_entry (2 in, 0 out)

```






### trap_obj_set_jump_motion

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 115 ; trap_obj_set_jump_motion (2 in, 0 out)

```






### trap_command_cage_on

_Format:_

```
syscall 1, 117 ; trap_command_cage_on (0 in, 0 out)

```






### trap_command_cage_off

_Format:_

```
syscall 1, 118 ; trap_command_cage_off (0 in, 0 out)

```






### trap_obj_check_step

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 119 ; trap_obj_check_step (4 in, 1 out)
pop unk ; unknown
```






### trap_target_pos

_Format:_

```
push unk1 ; unknown
syscall 1, 120 ; trap_target_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_target_search

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 121 ; trap_target_search (3 in, 0 out)

```






### trap_obj_dump

_Format:_

```
push unk1 ; unknown
syscall 1, 122 ; trap_obj_dump (1 in, 0 out)

```






### trap_obj_tex_fade_set

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 123 ; trap_obj_tex_fade_set (2 in, 0 out)

```






### trap_obj_is_entry_fly

_Format:_

```
push unk1 ; unknown
syscall 1, 124 ; trap_obj_is_entry_fly (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_tex_fade_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 125 ; trap_obj_tex_fade_start (4 in, 0 out)

```






### trap_obj_motion_sync

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 126 ; trap_obj_motion_sync (2 in, 0 out)

```






### trap_obj_act_clear

_Format:_

```
push unk1 ; unknown
syscall 1, 127 ; trap_obj_act_clear (1 in, 0 out)

```






### trap_obj_sysjump

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 128 ; trap_obj_sysjump (2 in, 0 out)

```






### trap_obj_blow

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 129 ; trap_obj_blow (2 in, 0 out)

```






### trap_obj_cmp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 130 ; trap_obj_cmp (2 in, 1 out)
pop unk ; unknown
```






### trap_target_dup

_Format:_

```
push unk1 ; unknown
syscall 1, 131 ; trap_target_dup (1 in, 1 out)
pop unk ; unknown
```






### trap_target_free

_Format:_

```
push unk1 ; unknown
syscall 1, 132 ; trap_target_free (1 in, 0 out)

```






### trap_obj_hide

_Format:_

```
push unk1 ; unknown
syscall 1, 133 ; trap_obj_hide (1 in, 0 out)

```






### trap_obj_show

_Format:_

```
push unk1 ; unknown
syscall 1, 134 ; trap_obj_show (1 in, 0 out)

```






### trap_bg_cross_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 135 ; trap_bg_cross_pos (4 in, 1 out)
pop unk ; unknown
```






### trap_bg_is_floor

_Format:_

```
push unk1 ; unknown
syscall 1, 136 ; trap_bg_is_floor (1 in, 1 out)
pop unk ; unknown
```






### trap_bg_get_normal

_Format:_

```
push unk1 ; unknown
syscall 1, 137 ; trap_bg_get_normal (1 in, 1 out)
pop unk ; unknown
```






### trap_pax_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 138 ; trap_pax_start (4 in, 1 out)
pop unk ; unknown
```






### trap_pax_start_bind

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 139 ; trap_pax_start_bind (5 in, 1 out)
pop unk ; unknown
```






### trap_target_is_exist

_Format:_

```
push unk1 ; unknown
syscall 1, 140 ; trap_target_is_exist (1 in, 1 out)
pop unk ; unknown
```






### trap_bg_ground_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 141 ; trap_bg_ground_pos (3 in, 1 out)
pop unk ; unknown
```






### trap_signal_reserve_min_hp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 142 ; trap_signal_reserve_min_hp (3 in, 0 out)

```






### trap_obj_search_by_serial

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 143 ; trap_obj_search_by_serial (2 in, 0 out)

```






### trap_obj_serial

_Format:_

```
push unk1 ; unknown
syscall 1, 144 ; trap_obj_serial (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_touch_zone

_Format:_

```
push unk1 ; unknown
syscall 1, 145 ; trap_obj_touch_zone (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_hitback

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 146 ; trap_obj_hitback (3 in, 0 out)

```






### trap_obj_pos

_Format:_

```
push unk1 ; unknown
syscall 1, 147 ; trap_obj_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 148 ; trap_obj_set_pos (2 in, 0 out)

```






### trap_obj_effect_start_bind_other

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 149 ; trap_obj_effect_start_bind_other (5 in, 1 out)
pop unk ; unknown
```






### trap_obj_motion_check_range

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 150 ; trap_obj_motion_check_range (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_motion_check_trigger

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 151 ; trap_obj_motion_check_trigger (2 in, 1 out)
pop unk ; unknown
```






### trap_status_is_mission

_Format:_

```
syscall 1, 152 ; trap_status_is_mission (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_reset_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 153 ; trap_obj_reset_pos (2 in, 0 out)

```






### trap_status_secure_mode_start

_Format:_

```
syscall 1, 154 ; trap_status_secure_mode_start (0 in, 0 out)

```






### trap_obj_add_hp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 155 ; trap_obj_add_hp (4 in, 1 out)
pop unk ; unknown
```






### trap_obj_hop

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
push unk6 ; unknown
push unk7 ; unknown
syscall 1, 156 ; trap_obj_hop (7 in, 0 out)

```






### trap_obj_camera_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 157 ; trap_obj_camera_start (3 in, 0 out)

```






### trap_bg_set_belt_conveyor

_Format:_

```
push unk1 ; unknown
syscall 1, 158 ; trap_bg_set_belt_conveyor (1 in, 0 out)

```






### trap_bg_set_uvscroll_speed

_Format:_

```
push unk1 ; unknown
syscall 1, 159 ; trap_bg_set_uvscroll_speed (1 in, 0 out)

```






### trap_target_set_obj

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 160 ; trap_target_set_obj (2 in, 0 out)

```






### trap_obj_is_attach

_Format:_

```
push unk1 ; unknown
syscall 1, 161 ; trap_obj_is_attach (1 in, 1 out)
pop unk ; unknown
```






### trap_target_set_before_player

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 162 ; trap_target_set_before_player (2 in, 0 out)

```






### trap_target_set_after_player

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 163 ; trap_target_set_after_player (2 in, 0 out)

```






### trap_obj_camera_start_global

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 164 ; trap_obj_camera_start_global (2 in, 0 out)

```






### trap_command_override

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 165 ; trap_command_override (4 in, 0 out)

```






### trap_target_attack

_Format:_

```
push unk1 ; unknown
syscall 1, 166 ; trap_target_attack (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_act_start_pri

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 167 ; trap_obj_act_start_pri (2 in, 0 out)

```






### trap_obj_flyjump

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 168 ; trap_obj_flyjump (5 in, 0 out)

```






### trap_obj_effect_unbind

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 169 ; trap_obj_effect_unbind (2 in, 0 out)

```






### trap_obj_unit_group

_Format:_

```
push unk1 ; unknown
syscall 1, 170 ; trap_obj_unit_group (1 in, 1 out)
pop unk ; unknown
```






### trap_status_no_leave

_Format:_

```
syscall 1, 171 ; trap_status_no_leave (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_can_look

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 172 ; trap_obj_can_look (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_can_look_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 173 ; trap_obj_can_look_pos (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_look_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 174 ; trap_obj_look_start (3 in, 0 out)

```






### trap_obj_look_start_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 175 ; trap_obj_look_start_pos (3 in, 0 out)

```






### trap_obj_look_end

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 176 ; trap_obj_look_end (2 in, 0 out)

```






### trap_obj_set_path

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 177 ; trap_obj_set_path (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_get_path_movement

_Format:_

```
push unk1 ; unknown
syscall 1, 178 ; trap_obj_get_path_movement (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_fall_motion

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 179 ; trap_obj_set_fall_motion (2 in, 0 out)

```






### trap_obj_set_land_motion

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 180 ; trap_obj_set_land_motion (2 in, 0 out)

```






### trap_light_create

_Format:_

```
push unk1 ; unknown
syscall 1, 181 ; trap_light_create (1 in, 1 out)
pop unk ; unknown
```






### trap_light_set_flag

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 182 ; trap_light_set_flag (2 in, 0 out)

```






### trap_light_set_color

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 183 ; trap_light_set_color (5 in, 0 out)

```






### trap_light_fadeout

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 184 ; trap_light_fadeout (2 in, 0 out)

```






### trap_obj_set_parts_color

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 185 ; trap_obj_set_parts_color (4 in, 0 out)

```






### trap_obj_reset_parts_color

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 186 ; trap_obj_reset_parts_color (3 in, 0 out)

```






### trap_status_prize_drain_start

_Format:_

```
syscall 1, 187 ; trap_status_prize_drain_start (0 in, 0 out)

```






### trap_status_prize_drain_end

_Format:_

```
syscall 1, 188 ; trap_status_prize_drain_end (0 in, 0 out)

```






### trap_obj_history_mark

_Format:_

```
push unk1 ; unknown
syscall 1, 189 ; trap_obj_history_mark (1 in, 0 out)

```






### trap_obj_is_history_mark

_Format:_

```
push unk1 ; unknown
syscall 1, 190 ; trap_obj_is_history_mark (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_lockon_target

_Format:_

```
push unk1 ; unknown
syscall 1, 191 ; trap_obj_lockon_target (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_is_motion_cancel

_Format:_

```
push unk1 ; unknown
syscall 1, 192 ; trap_obj_is_motion_cancel (1 in, 1 out)
pop unk ; unknown
```






### trap_camera_warp

_Format:_

```
syscall 1, 193 ; trap_camera_warp (0 in, 0 out)

```






### trap_obj_set_stealth

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 194 ; trap_obj_set_stealth (2 in, 0 out)

```






### trap_obj_reset_stealth

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 195 ; trap_obj_reset_stealth (2 in, 0 out)

```






### trap_area_entrance

_Format:_

```
syscall 1, 196 ; trap_area_entrance (0 in, 1 out)
pop unk ; unknown
```






### trap_area_cost_rest

_Format:_

```
syscall 1, 197 ; trap_area_cost_rest (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_player_random_pos

_Format:_

```
push unk1 ; unknown
syscall 1, 198 ; trap_obj_set_player_random_pos (1 in, 0 out)

```






### trap_obj_set_random_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 199 ; trap_obj_set_random_pos (4 in, 0 out)

```






### trap_obj_set_bg_collision_type

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 200 ; trap_obj_set_bg_collision_type (2 in, 0 out)

```






### trap_obj_dir

_Format:_

```
push unk1 ; unknown
syscall 1, 201 ; trap_obj_dir (1 in, 1 out)
pop unk ; unknown
```






### trap_unit_disable

_Format:_

```
push unk1 ; unknown
syscall 1, 202 ; trap_unit_disable (1 in, 0 out)

```






### trap_unit_enable

_Format:_

```
push unk1 ; unknown
syscall 1, 203 ; trap_unit_enable (1 in, 0 out)

```






### trap_status_force_leave_start

_Format:_

```
syscall 1, 204 ; trap_status_force_leave_start (0 in, 0 out)

```






### trap_status_force_leave_end

_Format:_

```
syscall 1, 205 ; trap_status_force_leave_end (0 in, 0 out)

```






### trap_status_is_force_leave

_Format:_

```
syscall 1, 206 ; trap_status_is_force_leave (0 in, 1 out)
pop unk ; unknown
```






### trap_camera_watch

_Format:_

```
push unk1 ; unknown
syscall 1, 207 ; trap_camera_watch (1 in, 0 out)

```






### trap_obj_is_hover

_Format:_

```
push unk1 ; unknown
syscall 1, 208 ; trap_obj_is_hover (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_dead

_Format:_

```
push unk1 ; unknown
syscall 1, 209 ; trap_obj_dead (1 in, 0 out)

```






### trap_obj_search_by_part

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 210 ; trap_obj_search_by_part (2 in, 0 out)

```






### trap_obj_pattern_enable

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 211 ; trap_obj_pattern_enable (2 in, 0 out)

```






### trap_obj_pattern_disable

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 212 ; trap_obj_pattern_disable (2 in, 0 out)

```






### trap_obj_part

_Format:_

```
push unk1 ; unknown
syscall 1, 213 ; trap_obj_part (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_hook_stop

_Format:_

```
push unk1 ; unknown
syscall 1, 214 ; trap_obj_hook_stop (1 in, 0 out)

```






### trap_obj_set_pos_trans

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 217 ; trap_obj_set_pos_trans (2 in, 0 out)

```






### trap_obj_set_unit_arg

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 218 ; trap_obj_set_unit_arg (3 in, 0 out)

```






### trap_obj_camera_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 219 ; trap_obj_camera_start (3 in, 0 out)

```






### trap_obj_move_to_space

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 220 ; trap_obj_move_to_space (3 in, 0 out)

```






### trap_obj_can_decide_command

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 221 ; trap_obj_can_decide_command (3 in, 1 out)
pop unk ; unknown
```






### trap_obj_get_entry_id

_Format:_

```
push unk1 ; unknown
syscall 1, 222 ; trap_obj_get_entry_id (1 in, 1 out)
pop unk ; unknown
```






### trap_camera_cancel

_Format:_

```
push unk1 ; unknown
syscall 1, 223 ; trap_camera_cancel (1 in, 0 out)

```






### trap_obj_is_action_air

_Format:_

```
push unk1 ; unknown
syscall 1, 224 ; trap_obj_is_action_air (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_is_star

_Format:_

```
push unk1 ; unknown
syscall 1, 225 ; trap_obj_is_star (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_scatter_prize_mu

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 226 ; trap_obj_scatter_prize_mu (2 in, 0 out)

```






### trap_obj_jump_direct

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 227 ; trap_obj_jump_direct (2 in, 0 out)

```






### trap_sheet_hp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 228 ; trap_sheet_hp (2 in, 1 out)
pop unk ; unknown
```






### trap_sheet_max_hp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 229 ; trap_sheet_max_hp (2 in, 1 out)
pop unk ; unknown
```






### trap_sheet_hp_rate

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 230 ; trap_sheet_hp_rate (2 in, 1 out)
pop unk ; unknown
```






### trap_sheet_set_min_hp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 231 ; trap_sheet_set_min_hp (3 in, 0 out)

```






### trap_sheet_min_hp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 232 ; trap_sheet_min_hp (2 in, 1 out)
pop unk ; unknown
```






### trap_sheet_set_hp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 233 ; trap_sheet_set_hp (3 in, 0 out)

```






### trap_party_get_weapon

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 234 ; trap_party_get_weapon (2 in, 1 out)
pop unk ; unknown
```






### trap_party_hand_to_bone

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 235 ; trap_party_hand_to_bone (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_motion_unsync

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 236 ; trap_obj_motion_unsync (2 in, 0 out)

```






### trap_command_override_top

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 237 ; trap_command_override_top (5 in, 0 out)

```






### trap_obj_motion_capture_id

_Format:_

```
push unk1 ; unknown
syscall 1, 238 ; trap_obj_motion_capture_id (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_is_unit_active

_Format:_

```
push unk1 ; unknown
syscall 1, 239 ; trap_obj_is_unit_active (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_scatter_prize_tt

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 240 ; trap_obj_scatter_prize_tt (3 in, 0 out)

```






### trap_act_shout

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 241 ; trap_act_shout (2 in, 0 out)

```






### trap_player_capture_form

_Format:_

```
push unk1 ; unknown
syscall 1, 242 ; trap_player_capture_form (1 in, 0 out)

```






### trap_player_capture_form_end

_Format:_

```
syscall 1, 243 ; trap_player_capture_form_end (0 in, 0 out)

```






### trap_status_is_battle

_Format:_

```
syscall 1, 244 ; trap_status_is_battle (0 in, 1 out)
pop unk ; unknown
```






### trap_target_clear_before_player

_Format:_

```
syscall 1, 245 ; trap_target_clear_before_player (0 in, 0 out)

```






### trap_target_clear_after_player

_Format:_

```
syscall 1, 246 ; trap_target_clear_after_player (0 in, 0 out)

```






### trap_bg_get_random_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 247 ; trap_bg_get_random_pos (3 in, 1 out)
pop unk ; unknown
```






### trap_bg_get_random_pos_air

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 248 ; trap_bg_get_random_pos_air (5 in, 1 out)
pop unk ; unknown
```






### trap_status_set_prize_ratio

_Format:_

```
push unk1 ; unknown
syscall 1, 249 ; trap_status_set_prize_ratio (1 in, 0 out)

```






### trap_status_set_lockon_ratio

_Format:_

```
push unk1 ; unknown
syscall 1, 250 ; trap_status_set_lockon_ratio (1 in, 0 out)

```






### trap_light_fadein

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 251 ; trap_light_fadein (2 in, 0 out)

```






### trap_camera_apply_pos

_Format:_

```
push unk1 ; unknown
syscall 1, 252 ; trap_camera_apply_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_can_capture_control

_Format:_

```
push unk1 ; unknown
syscall 1, 253 ; trap_obj_can_capture_control (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_is_ride

_Format:_

```
push unk1 ; unknown
syscall 1, 254 ; trap_obj_is_ride (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_disable_occ

_Format:_

```
push unk1 ; unknown
syscall 1, 255 ; trap_obj_disable_occ (1 in, 0 out)

```






### trap_obj_enable_occ

_Format:_

```
push unk1 ; unknown
syscall 1, 256 ; trap_obj_enable_occ (1 in, 0 out)

```






### trap_light_set_fog_near

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 257 ; trap_light_set_fog_near (2 in, 0 out)

```






### trap_light_set_fog_far

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 258 ; trap_light_set_fog_far (2 in, 0 out)

```






### trap_light_set_fog_min

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 259 ; trap_light_set_fog_min (2 in, 0 out)

```






### trap_light_set_fog_max

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 260 ; trap_light_set_fog_max (2 in, 0 out)

```






### trap_sheet_munny

_Format:_

```
syscall 1, 261 ; trap_sheet_munny (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_voice

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 262 ; trap_obj_voice (3 in, 0 out)

```






### trap_player_set_exec_rc

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 263 ; trap_player_set_exec_rc (2 in, 0 out)

```






### trap_status_secure_mode_end

_Format:_

```
syscall 1, 264 ; trap_status_secure_mode_end (0 in, 0 out)

```






### trap_obj_set_medal

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 265 ; trap_obj_set_medal (2 in, 0 out)

```






### trap_obj_get_medal

_Format:_

```
push unk1 ; unknown
syscall 1, 266 ; trap_obj_get_medal (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_scatter_medal

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 267 ; trap_obj_scatter_medal (2 in, 0 out)

```






### trap_obj_action_lightcycle

_Format:_

```
push unk1 ; unknown
syscall 1, 268 ; trap_obj_action_lightcycle (1 in, 0 out)

```






### trap_obj_get_lightcycle_movement

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 269 ; trap_obj_get_lightcycle_movement (3 in, 1 out)
pop unk ; unknown
```






### trap_obj_motion_disable_anmatr_effect

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 270 ; trap_obj_motion_disable_anmatr_effect (2 in, 0 out)

```






### trap_obj_motion_enable_anmatr_effect

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 271 ; trap_obj_motion_enable_anmatr_effect (2 in, 0 out)

```






### trap_obj_is_dead

_Format:_

```
push unk1 ; unknown
syscall 1, 272 ; trap_obj_is_dead (1 in, 1 out)
pop unk ; unknown
```






### trap_signal_hook

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 273 ; trap_signal_hook (2 in, 0 out)

```






### trap_event_get_rest_time

_Format:_

```
syscall 1, 274 ; trap_event_get_rest_time (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_recov_holylight

_Format:_

```
push unk1 ; unknown
syscall 1, 275 ; trap_obj_recov_holylight (1 in, 0 out)

```






### trap_obj_use_mp

_Format:_

```
push unk1 ; unknown
syscall 1, 276 ; trap_obj_use_mp (1 in, 0 out)

```






### trap_obj_reraise

_Format:_

```
push unk1 ; unknown
syscall 1, 277 ; trap_obj_reraise (1 in, 0 out)

```






### trap_obj_scatter_prize_tr

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 278 ; trap_obj_scatter_prize_tr (2 in, 0 out)

```






### trap_prize_appear_tr

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 279 ; trap_prize_appear_tr (2 in, 0 out)

```






### trap_sheet_add_munny

_Format:_

```
push unk1 ; unknown
syscall 1, 280 ; trap_sheet_add_munny (1 in, 1 out)
pop unk ; unknown
```






### trap_camera_begin_scope

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 281 ; trap_camera_begin_scope (2 in, 0 out)

```






### trap_camera_end_scope

_Format:_

```
syscall 1, 283 ; trap_camera_end_scope (0 in, 0 out)

```






### trap_tutorial_pause

_Format:_

```
push unk1 ; unknown
syscall 1, 284 ; trap_tutorial_pause (1 in, 0 out)

```






### trap_obj_show_picture

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 285 ; trap_obj_show_picture (2 in, 1 out)
pop unk ; unknown
```






### trap_status_hide_shadow

_Format:_

```
syscall 1, 286 ; trap_status_hide_shadow (0 in, 0 out)

```






### trap_status_show_shadow

_Format:_

```
syscall 1, 287 ; trap_status_show_shadow (0 in, 0 out)

```






### trap_status_begin_free_ability

_Format:_

```
syscall 1, 288 ; trap_status_begin_free_ability (0 in, 0 out)

```






### trap_status_end_free_ability

_Format:_

```
syscall 1, 289 ; trap_status_end_free_ability (0 in, 0 out)

```






### trap_picture_change

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 290 ; trap_picture_change (2 in, 0 out)

```






### trap_obj_levelup_unit

_Format:_

```
push unk1 ; unknown
syscall 1, 291 ; trap_obj_levelup_unit (1 in, 0 out)

```






### trap_obj_search_by_unit_arg

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 292 ; trap_obj_search_by_unit_arg (3 in, 0 out)

```






### trap_event_control_off

_Format:_

```
syscall 1, 293 ; trap_event_control_off (0 in, 0 out)

```






### trap_event_control_on

_Format:_

```
syscall 1, 294 ; trap_event_control_on (0 in, 0 out)

```






### trap_camera_reset

_Format:_

```
syscall 1, 295 ; trap_camera_reset (0 in, 0 out)

```






### trap_tutorial_open

_Format:_

```
push unk1 ; unknown
syscall 1, 296 ; trap_tutorial_open (1 in, 0 out)

```






### trap_player_get_rc

_Format:_

```
push unk1 ; unknown
syscall 1, 297 ; trap_player_get_rc (1 in, 1 out)
pop unk ; unknown
```






### trap_worldwork_get

_Format:_

```
syscall 1, 298 ; trap_worldwork_get (0 in, 1 out)
pop unk ; unknown
```






### trap_area_set_next_entrance

_Format:_

```
syscall 1, 299 ; trap_area_set_next_entrance (0 in, 0 out)

```






### trap_prize_num

_Format:_

```
syscall 1, 300 ; trap_prize_num (0 in, 1 out)
pop unk ; unknown
```






### trap_tutorial_is_open

_Format:_

```
syscall 1, 301 ; trap_tutorial_is_open (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_skateboard_mode

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 302 ; trap_obj_set_skateboard_mode (2 in, 0 out)

```






### trap_area_cost_ratio

_Format:_

```
syscall 1, 303 ; trap_area_cost_ratio (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_search_by_glance

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 304 ; trap_obj_search_by_glance (2 in, 0 out)

```






### trap_camera_eye

_Format:_

```
syscall 1, 305 ; trap_camera_eye (0 in, 1 out)
pop unk ; unknown
```






### trap_camera_at

_Format:_

```
syscall 1, 306 ; trap_camera_at (0 in, 1 out)
pop unk ; unknown
```






### trap_obj_search_by_camera

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 307 ; trap_obj_search_by_camera (2 in, 0 out)

```






### trap_obj_capture_command

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 308 ; trap_obj_capture_command (2 in, 0 out)

```






### trap_sysobj_is_player

_Format:_

```
push unk1 ; unknown
syscall 1, 309 ; trap_sysobj_is_player (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_get_weight

_Format:_

```
push unk1 ; unknown
syscall 1, 310 ; trap_obj_get_weight (1 in, 1 out)
pop unk ; unknown
```






### trap_sheet_set_element_rate

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 311 ; trap_sheet_set_element_rate (3 in, 0 out)

```






### trap_camera_set_scope_zoom

_Format:_

```
push unk1 ; unknown
syscall 1, 312 ; trap_camera_set_scope_zoom (1 in, 0 out)

```






### trap_camera_set_scope_closeup_distance

_Format:_

```
push unk1 ; unknown
syscall 1, 313 ; trap_camera_set_scope_closeup_distance (1 in, 0 out)

```






### trap_camera_set_scope_target_pos

_Format:_

```
push unk1 ; unknown
syscall 1, 314 ; trap_camera_set_scope_target_pos (1 in, 0 out)

```






### trap_picture_set_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 315 ; trap_picture_set_pos (3 in, 0 out)

```






### trap_camera_get_projection_pos

_Format:_

```
push unk1 ; unknown
syscall 1, 316 ; trap_camera_get_projection_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_status_no_gameover

_Format:_

```
syscall 1, 317 ; trap_status_no_gameover (0 in, 0 out)

```






### trap_obj_play_se

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 318 ; trap_obj_play_se (2 in, 0 out)

```






### trap_sysobj_is_sora

_Format:_

```
push unk1 ; unknown
syscall 1, 319 ; trap_sysobj_is_sora (1 in, 1 out)
pop unk ; unknown
```






### trap_unit_get_enemy_num

_Format:_

```
syscall 1, 320 ; trap_unit_get_enemy_num (0 in, 1 out)
pop unk ; unknown
```






### trap_player_lockon

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 321 ; trap_player_lockon (3 in, 0 out)

```






### trap_command_enable_item

_Format:_

```
syscall 1, 322 ; trap_command_enable_item (0 in, 0 out)

```






### trap_obj_count_entry

_Format:_

```
push unk1 ; unknown
syscall 1, 323 ; trap_obj_count_entry (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_pattern_reset

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 324 ; trap_obj_pattern_reset (2 in, 0 out)

```






### trap_obj_reaction_callback

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 325 ; trap_obj_reaction_callback (4 in, 0 out)

```






### trap_bg_set_animation_speed

_Format:_

```
push unk1 ; unknown
syscall 1, 326 ; trap_bg_set_animation_speed (1 in, 0 out)

```






### trap_prize_get_all_tr

_Format:_

```
push unk1 ; unknown
syscall 1, 327 ; trap_prize_get_all_tr (1 in, 0 out)

```






### trap_obj_dead_mark

_Format:_

```
push unk1 ; unknown
syscall 1, 328 ; trap_obj_dead_mark (1 in, 0 out)

```






### trap_sheet_set_prize_range

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 329 ; trap_sheet_set_prize_range (2 in, 0 out)

```






### trap_obj_set_cannon_camera_offset

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 330 ; trap_obj_set_cannon_camera_offset (3 in, 0 out)

```






### trap_obj_each_all

_Format:_

```
push unk1 ; unknown
syscall 1, 331 ; trap_obj_each_all (1 in, 1 out)
pop unk ; unknown
```






### trap_sysobj_is_btlnpc

_Format:_

```
push unk1 ; unknown
syscall 1, 332 ; trap_sysobj_is_btlnpc (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_cannon_param

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 1, 333 ; trap_obj_set_cannon_param (5 in, 0 out)

```






### trap_command_enable

_Format:_

```
syscall 1, 334 ; trap_command_enable (0 in, 0 out)

```






### trap_obj_disable_occ_bone

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 335 ; trap_obj_disable_occ_bone (2 in, 0 out)

```






### trap_obj_enable_occ_bone

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 336 ; trap_obj_enable_occ_bone (2 in, 0 out)

```






### trap_command_set_side_b

_Format:_

```
syscall 1, 337 ; trap_command_set_side_b (0 in, 0 out)

```






### trap_prize_return_ca

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 338 ; trap_prize_return_ca (3 in, 1 out)
pop unk ; unknown
```






### trap_prize_vacuum_ca

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 339 ; trap_prize_vacuum_ca (3 in, 1 out)
pop unk ; unknown
```






### trap_prize_vacuum_range_ca

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 340 ; trap_prize_vacuum_range_ca (2 in, 0 out)

```






### trap_prize_num_ca

_Format:_

```
syscall 1, 341 ; trap_prize_num_ca (0 in, 1 out)
pop unk ; unknown
```






### trap_prize_appear_num

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 342 ; trap_prize_appear_num (3 in, 0 out)

```






### trap_obj_is_equip_ability

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 343 ; trap_obj_is_equip_ability (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_clear_occ

_Format:_

```
push unk1 ; unknown
syscall 1, 344 ; trap_obj_clear_occ (1 in, 0 out)

```






### trap_command_override_slot

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 1, 345 ; trap_command_override_slot (4 in, 1 out)
pop unk ; unknown
```






### trap_command_slot_set_status

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 346 ; trap_command_slot_set_status (2 in, 0 out)

```






### trap_obj_can_see

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 347 ; trap_obj_can_see (2 in, 1 out)
pop unk ; unknown
```






### trap_sheet_set_hitback_addition

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 348 ; trap_sheet_set_hitback_addition (2 in, 0 out)

```






### trap_obj_effect_kill_all

_Format:_

```
push unk1 ; unknown
syscall 1, 349 ; trap_obj_effect_kill_all (1 in, 0 out)

```






### trap_status_close_pete_curtain

_Format:_

```
syscall 1, 350 ; trap_status_close_pete_curtain (0 in, 0 out)

```






### trap_status_open_pete_curtain

_Format:_

```
syscall 1, 351 ; trap_status_open_pete_curtain (0 in, 0 out)

```






### trap_area_set_return_tr

_Format:_

```
syscall 1, 352 ; trap_area_set_return_tr (0 in, 0 out)

```






### trap_obj_start_mpdrive

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 353 ; trap_obj_start_mpdrive (2 in, 0 out)

```






### trap_event_layer_off

_Format:_

```
syscall 1, 354 ; trap_event_layer_off (0 in, 0 out)

```






### trap_player_can_capture_form

_Format:_

```
syscall 1, 355 ; trap_player_can_capture_form (0 in, 1 out)
pop unk ; unknown
```






### trap_event_layer_on

_Format:_

```
syscall 1, 356 ; trap_event_layer_on (0 in, 0 out)

```






### trap_sheet_attack_level

_Format:_

```
push unk1 ; unknown
syscall 1, 357 ; trap_sheet_attack_level (1 in, 1 out)
pop unk ; unknown
```






### trap_sheet_set_attack_level

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 358 ; trap_sheet_set_attack_level (2 in, 0 out)

```






### trap_obj_hook_command_image

_Format:_

```
push unk1 ; unknown
syscall 1, 359 ; trap_obj_hook_command_image (1 in, 0 out)

```






### trap_obj_reset_command_image

_Format:_

```
push unk1 ; unknown
syscall 1, 360 ; trap_obj_reset_command_image (1 in, 0 out)

```






### trap_sheet_level

_Format:_

```
push unk1 ; unknown
syscall 1, 361 ; trap_sheet_level (1 in, 1 out)
pop unk ; unknown
```






### trap_treasure_get

_Format:_

```
push unk1 ; unknown
syscall 1, 362 ; trap_treasure_get (1 in, 0 out)

```






### trap_prize_appear_xaldin

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 363 ; trap_prize_appear_xaldin (2 in, 0 out)

```






### trap_jigsaw_get

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 1, 364 ; trap_jigsaw_get (2 in, 0 out)

```






### trap_command_disable_group

_Format:_

```
push unk1 ; unknown
syscall 1, 365 ; trap_command_disable_group (1 in, 0 out)

```






### trap_command_enable_group

_Format:_

```
push unk1 ; unknown
syscall 1, 366 ; trap_command_enable_group (1 in, 0 out)

```






### trap_obj_get_move_to_space_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 1, 367 ; trap_obj_get_move_to_space_pos (3 in, 1 out)
pop unk ; unknown
```






### trap_enemy_exec_damage

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 0 ; trap_enemy_exec_damage (2 in, 0 out)

```






### trap_enemy_exec_damage_blow

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
push unk6 ; unknown
syscall 2, 1 ; trap_enemy_exec_damage_blow (6 in, 0 out)

```






### trap_enemy_exec_damage_small

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 2, 2 ; trap_enemy_exec_damage_small (3 in, 0 out)

```






### trap_enemy_exec_damage_hitback

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 2, 3 ; trap_enemy_exec_damage_hitback (3 in, 0 out)

```






### trap_enemy_each

_Format:_

```
push unk1 ; unknown
syscall 2, 4 ; trap_enemy_each (1 in, 1 out)
pop unk ; unknown
```






### trap_enemy_is_no_control

_Format:_

```
push unk1 ; unknown
syscall 2, 5 ; trap_enemy_is_no_control (1 in, 1 out)
pop unk ; unknown
```






### trap_enemy_is_damage_motion

_Format:_

```
push unk1 ; unknown
syscall 2, 6 ; trap_enemy_is_damage_motion (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_reaction

_Format:_

```
push unk1 ; unknown
syscall 2, 7 ; trap_damage_reaction (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_is_reaction

_Format:_

```
push unk1 ; unknown
syscall 2, 8 ; trap_damage_is_reaction (1 in, 1 out)
pop unk ; unknown
```






### trap_btlobj_set_sheet

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 2, 9 ; trap_btlobj_set_sheet (3 in, 0 out)

```






### trap_attack_new

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 2, 10 ; trap_attack_new (4 in, 1 out)
pop unk ; unknown
```






### trap_attack_set_radius

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 2, 11 ; trap_attack_set_radius (3 in, 0 out)

```






### trap_attack_set_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 12 ; trap_attack_set_pos (2 in, 0 out)

```






### trap_attack_free

_Format:_

```
push unk1 ; unknown
syscall 2, 13 ; trap_attack_free (1 in, 0 out)

```






### trap_attack_is_hit

_Format:_

```
push unk1 ; unknown
syscall 2, 14 ; trap_attack_is_hit (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_exec_reaction

_Format:_

```
push unk1 ; unknown
syscall 2, 15 ; trap_damage_exec_reaction (1 in, 0 out)

```






### trap_damage_is_exec_reaction

_Format:_

```
push unk1 ; unknown
syscall 2, 16 ; trap_damage_is_exec_reaction (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_strike

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 2, 17 ; trap_attack_strike (4 in, 0 out)

```






### trap_attack_is_strike

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 18 ; trap_attack_is_strike (2 in, 1 out)
pop unk ; unknown
```






### trap_attack_set_line

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 2, 19 ; trap_attack_set_line (3 in, 0 out)

```






### trap_magic_start_thread

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 20 ; trap_magic_start_thread (2 in, 1 out)
pop unk ; unknown
```






### trap_teamwork_alloc

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 21 ; trap_teamwork_alloc (2 in, 1 out)
pop unk ; unknown
```






### trap_attack_set_obj_pax

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 22 ; trap_attack_set_obj_pax (2 in, 0 out)

```






### trap_btlobj_target

_Format:_

```
push unk1 ; unknown
syscall 2, 23 ; trap_btlobj_target (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_get_owner

_Format:_

```
push unk1 ; unknown
syscall 2, 24 ; trap_attack_get_owner (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_get_param_id

_Format:_

```
push unk1 ; unknown
syscall 2, 25 ; trap_attack_get_param_id (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_exec_reflect

_Format:_

```
push unk1 ; unknown
syscall 2, 26 ; trap_attack_exec_reflect (1 in, 0 out)

```






### trap_enemy_exec_reflect

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 2, 27 ; trap_enemy_exec_reflect (5 in, 0 out)

```






### trap_attack_refresh

_Format:_

```
push unk1 ; unknown
syscall 2, 28 ; trap_attack_refresh (1 in, 0 out)

```






### trap_attack_is_hit_bg

_Format:_

```
push unk1 ; unknown
syscall 2, 29 ; trap_attack_is_hit_bg (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_set_pax

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 30 ; trap_attack_set_pax (2 in, 0 out)

```






### trap_attack_dup

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 31 ; trap_attack_dup (2 in, 1 out)
pop unk ; unknown
```






### trap_damage_blow_up

_Format:_

```
push unk1 ; unknown
syscall 2, 32 ; trap_damage_blow_up (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_blow_speed

_Format:_

```
push unk1 ; unknown
syscall 2, 33 ; trap_damage_blow_speed (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_get_type

_Format:_

```
push unk1 ; unknown
syscall 2, 34 ; trap_attack_get_type (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_attack_type

_Format:_

```
push unk1 ; unknown
syscall 2, 35 ; trap_damage_attack_type (1 in, 1 out)
pop unk ; unknown
```






### trap_enemy_add_damage

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 36 ; trap_enemy_add_damage (2 in, 0 out)

```






### trap_attack_set_team

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 37 ; trap_attack_set_team (2 in, 0 out)

```






### trap_attack_set_hit_callback

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 2, 38 ; trap_attack_set_hit_callback (3 in, 0 out)

```






### trap_attack_is_reflect

_Format:_

```
push unk1 ; unknown
syscall 2, 39 ; trap_attack_is_reflect (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_is_hit_wall

_Format:_

```
push unk1 ; unknown
syscall 2, 40 ; trap_attack_is_hit_wall (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_is_hit_floor

_Format:_

```
push unk1 ; unknown
syscall 2, 41 ; trap_attack_is_hit_floor (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_hit_bg_pos

_Format:_

```
push unk1 ; unknown
syscall 2, 42 ; trap_attack_hit_bg_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_get_reflect_vector

_Format:_

```
push unk1 ; unknown
syscall 2, 43 ; trap_attack_get_reflect_vector (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_reflecter

_Format:_

```
push unk1 ; unknown
syscall 2, 44 ; trap_attack_reflecter (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_attack_param_id

_Format:_

```
push unk1 ; unknown
syscall 2, 45 ; trap_damage_attack_param_id (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_damage

_Format:_

```
push unk1 ; unknown
syscall 2, 46 ; trap_damage_damage (1 in, 1 out)
pop unk ; unknown
```






### trap_limit_motion_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 2, 47 ; trap_limit_motion_start (4 in, 1 out)
pop unk ; unknown
```






### trap_limit_player

_Format:_

```
push unk1 ; unknown
syscall 2, 48 ; trap_limit_player (1 in, 1 out)
pop unk ; unknown
```






### trap_limit_friend

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 49 ; trap_limit_friend (2 in, 1 out)
pop unk ; unknown
```






### trap_limit_camera_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 2, 50 ; trap_limit_camera_start (4 in, 0 out)

```






### trap_attack_set_rc

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
syscall 2, 51 ; trap_attack_set_rc (5 in, 0 out)

```






### trap_attack_rc_receiver

_Format:_

```
push unk1 ; unknown
syscall 2, 52 ; trap_attack_rc_receiver (1 in, 1 out)
pop unk ; unknown
```






### trap_enemy_last_dead

_Format:_

```
syscall 2, 53 ; trap_enemy_last_dead (0 in, 1 out)
pop unk ; unknown
```






### trap_limit_start_thread

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 54 ; trap_limit_start_thread (2 in, 0 out)

```






### trap_limit_light

_Format:_

```
push unk1 ; unknown
syscall 2, 55 ; trap_limit_light (1 in, 1 out)
pop unk ; unknown
```






### trap_btlobj_lockon_target

_Format:_

```
push unk1 ; unknown
syscall 2, 56 ; trap_btlobj_lockon_target (1 in, 1 out)
pop unk ; unknown
```






### trap_limit_effect_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 2, 57 ; trap_limit_effect_start (3 in, 1 out)
pop unk ; unknown
```






### trap_limit_effect_start_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 2, 58 ; trap_limit_effect_start_pos (4 in, 1 out)
pop unk ; unknown
```






### trap_limit_effect_start_bind

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 2, 59 ; trap_limit_effect_start_bind (4 in, 1 out)
pop unk ; unknown
```






### trap_limit_time

_Format:_

```
push unk1 ; unknown
syscall 2, 60 ; trap_limit_time (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_set_effect

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 61 ; trap_attack_set_effect (2 in, 0 out)

```






### trap_attack_set_time

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 2, 62 ; trap_attack_set_time (4 in, 0 out)

```






### trap_limit_reference

_Format:_

```
push unk1 ; unknown
syscall 2, 63 ; trap_limit_reference (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_orig_reaction

_Format:_

```
push unk1 ; unknown
syscall 2, 64 ; trap_damage_orig_reaction (1 in, 1 out)
pop unk ; unknown
```






### trap_enemy_count_damager

_Format:_

```
syscall 2, 65 ; trap_enemy_count_damager (0 in, 1 out)
pop unk ; unknown
```






### trap_attack_get_reflect_count

_Format:_

```
push unk1 ; unknown
syscall 2, 66 ; trap_attack_get_reflect_count (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_new_combo_group

_Format:_

```
syscall 2, 67 ; trap_attack_new_combo_group (0 in, 1 out)
pop unk ; unknown
```






### trap_magic_set_cost

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 68 ; trap_magic_set_cost (2 in, 0 out)

```






### trap_magic_can_add_cost

_Format:_

```
push unk1 ; unknown
syscall 2, 69 ; trap_magic_can_add_cost (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_parts

_Format:_

```
push unk1 ; unknown
syscall 2, 70 ; trap_damage_parts (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_set_hitmark_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 71 ; trap_attack_set_hitmark_pos (2 in, 0 out)

```






### trap_damage_is_cure

_Format:_

```
push unk1 ; unknown
syscall 2, 72 ; trap_damage_is_cure (1 in, 1 out)
pop unk ; unknown
```






### trap_bonuslevel_up

_Format:_

```
push unk1 ; unknown
syscall 2, 73 ; trap_bonuslevel_up (1 in, 0 out)

```






### trap_attack_set_reflect_callback

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 2, 74 ; trap_attack_set_reflect_callback (3 in, 0 out)

```






### trap_summon_is_tink_exist

_Format:_

```
syscall 2, 75 ; trap_summon_is_tink_exist (0 in, 1 out)
pop unk ; unknown
```






### trap_enemy_set_karma_limit

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 76 ; trap_enemy_set_karma_limit (2 in, 0 out)

```






### trap_vacuum_create

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 77 ; trap_vacuum_create (2 in, 1 out)
pop unk ; unknown
```






### trap_vacuum_destroy

_Format:_

```
push unk1 ; unknown
syscall 2, 78 ; trap_vacuum_destroy (1 in, 0 out)

```






### trap_vacuum_set_ignore_type

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 79 ; trap_vacuum_set_ignore_type (2 in, 0 out)

```






### trap_vacuum_set_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 80 ; trap_vacuum_set_pos (2 in, 0 out)

```






### trap_vacuum_set_speed

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 2, 81 ; trap_vacuum_set_speed (4 in, 0 out)

```






### trap_vacuum_set_rot_speed

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 82 ; trap_vacuum_set_rot_speed (2 in, 0 out)

```






### trap_vacuum_set_near_range

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 83 ; trap_vacuum_set_near_range (2 in, 0 out)

```






### trap_vacuum_set_dist_rate

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 84 ; trap_vacuum_set_dist_rate (2 in, 0 out)

```






### trap_damage_element

_Format:_

```
push unk1 ; unknown
syscall 2, 85 ; trap_damage_element (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_get_hitback

_Format:_

```
push unk1 ; unknown
syscall 2, 86 ; trap_damage_get_hitback (1 in, 1 out)
pop unk ; unknown
```






### trap_enemy_exec_damage_large

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 2, 87 ; trap_enemy_exec_damage_large (3 in, 0 out)

```






### trap_enemy_get_attacker

_Format:_

```
push unk1 ; unknown
syscall 2, 88 ; trap_enemy_get_attacker (1 in, 1 out)
pop unk ; unknown
```






### trap_limit_reset_special_command

_Format:_

```
push unk1 ; unknown
syscall 2, 89 ; trap_limit_reset_special_command (1 in, 0 out)

```






### trap_limit_close_gauge

_Format:_

```
push unk1 ; unknown
syscall 2, 90 ; trap_limit_close_gauge (1 in, 0 out)

```






### trap_damage_get_reaction_type

_Format:_

```
push unk1 ; unknown
syscall 2, 91 ; trap_damage_get_reaction_type (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_is_finish

_Format:_

```
push unk1 ; unknown
syscall 2, 92 ; trap_damage_is_finish (1 in, 1 out)
pop unk ; unknown
```






### trap_damage_is_normal

_Format:_

```
push unk1 ; unknown
syscall 2, 93 ; trap_damage_is_normal (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_set_system_pax

_Format:_

```
push unk1 ; unknown
syscall 2, 94 ; trap_attack_set_system_pax (1 in, 0 out)

```






### trap_btlobj_dup_sheet

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 95 ; trap_btlobj_dup_sheet (2 in, 0 out)

```






### trap_attack_is_valid

_Format:_

```
push unk1 ; unknown
syscall 2, 96 ; trap_attack_is_valid (1 in, 1 out)
pop unk ; unknown
```






### trap_enemy_set_attacker

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 2, 97 ; trap_enemy_set_attacker (2 in, 0 out)

```






### trap_event_is_exec

_Format:_

```
syscall 4, 2 ; trap_event_is_exec (0 in, 1 out)
pop unk ; unknown
```






### trap_mission_complete

_Format:_

```
push unk1 ; unknown
syscall 4, 3 ; trap_mission_complete (1 in, 0 out)

```






### trap_mission_information

_Format:_

```
push unk1 ; unknown
syscall 4, 4 ; trap_mission_information (1 in, 0 out)

```






### trap_mission_set_count

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 5 ; trap_mission_set_count (2 in, 0 out)

```






### trap_mission_increment_count

_Format:_

```
push unk1 ; unknown
syscall 4, 6 ; trap_mission_increment_count (1 in, 0 out)

```






### trap_mission_restart_timer

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 7 ; trap_mission_restart_timer (2 in, 0 out)

```






### trap_mission_set_gauge

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 8 ; trap_mission_set_gauge (2 in, 0 out)

```






### trap_mission_add_gauge

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 9 ; trap_mission_add_gauge (2 in, 0 out)

```






### trap_mission_set_gauge_ratio

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 10 ; trap_mission_set_gauge_ratio (2 in, 0 out)

```






### trap_mission_failed

_Format:_

```
syscall 4, 11 ; trap_mission_failed (0 in, 0 out)

```






### trap_mission_get_gauge_ratio

_Format:_

```
push unk1 ; unknown
syscall 4, 12 ; trap_mission_get_gauge_ratio (1 in, 1 out)
pop unk ; unknown
```






### trap_mission_pause_timer

_Format:_

```
syscall 4, 13 ; trap_mission_pause_timer (0 in, 0 out)

```






### trap_mission_activate2d

_Format:_

```
syscall 4, 14 ; trap_mission_activate2d (0 in, 0 out)

```






### trap_mission_deactivate2d

_Format:_

```
syscall 4, 15 ; trap_mission_deactivate2d (0 in, 0 out)

```






### trap_mission_dead_boss

_Format:_

```
push unk1 ; unknown
syscall 4, 16 ; trap_mission_dead_boss (1 in, 0 out)

```






### trap_mission_set_timer_param

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 4, 17 ; trap_mission_set_timer_param (4 in, 0 out)

```






### trap_mission_set_count_param

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 4, 18 ; trap_mission_set_count_param (4 in, 0 out)

```






### trap_mission_set_gauge_param

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 4, 19 ; trap_mission_set_gauge_param (4 in, 0 out)

```






### trap_mission_decrement_count

_Format:_

```
push unk1 ; unknown
syscall 4, 20 ; trap_mission_decrement_count (1 in, 0 out)

```






### trap_mission_is_activate2d

_Format:_

```
syscall 4, 21 ; trap_mission_is_activate2d (0 in, 1 out)
pop unk ; unknown
```






### trap_mission_exit

_Format:_

```
push unk1 ; unknown
syscall 4, 22 ; trap_mission_exit (1 in, 0 out)

```






### trap_mission_reset_pause_mode

_Format:_

```
syscall 4, 23 ; trap_mission_reset_pause_mode (0 in, 0 out)

```






### trap_mission_cancel_pause_timer

_Format:_

```
syscall 4, 24 ; trap_mission_cancel_pause_timer (0 in, 0 out)

```






### trap_mission_start_combo_counter

_Format:_

```
push unk1 ; unknown
syscall 4, 25 ; trap_mission_start_combo_counter (1 in, 0 out)

```






### trap_mission_get_timer

_Format:_

```
push unk1 ; unknown
syscall 4, 26 ; trap_mission_get_timer (1 in, 1 out)
pop unk ; unknown
```






### trap_mission_stop_combo_counter

_Format:_

```
syscall 4, 27 ; trap_mission_stop_combo_counter (0 in, 0 out)

```






### trap_mission_get_gauge_warning_ratio

_Format:_

```
push unk1 ; unknown
syscall 4, 28 ; trap_mission_get_gauge_warning_ratio (1 in, 1 out)
pop unk ; unknown
```






### trap_mission_get_count

_Format:_

```
push unk1 ; unknown
syscall 4, 29 ; trap_mission_get_count (1 in, 1 out)
pop unk ; unknown
```






### trap_mission_get_max_combo_counter

_Format:_

```
syscall 4, 30 ; trap_mission_get_max_combo_counter (0 in, 1 out)
pop unk ; unknown
```






### trap_mission_get_combo_counter

_Format:_

```
syscall 4, 31 ; trap_mission_get_combo_counter (0 in, 1 out)
pop unk ; unknown
```






### trap_mission_return

_Format:_

```
syscall 4, 32 ; trap_mission_return (0 in, 0 out)

```






### trap_mission_add_combo_counter

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 33 ; trap_mission_add_combo_counter (2 in, 0 out)

```






### trap_mission_is_gauge_warning

_Format:_

```
push unk1 ; unknown
syscall 4, 34 ; trap_mission_is_gauge_warning (1 in, 1 out)
pop unk ; unknown
```






### trap_score_type

_Format:_

```
push unk1 ; unknown
syscall 4, 35 ; trap_score_type (1 in, 1 out)
pop unk ; unknown
```






### trap_score_score

_Format:_

```
push unk1 ; unknown
syscall 4, 36 ; trap_score_score (1 in, 1 out)
pop unk ; unknown
```






### trap_score_update

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 4, 37 ; trap_score_update (3 in, 1 out)
pop unk ; unknown
```






### trap_score_get

_Format:_

```
push unk1 ; unknown
syscall 4, 38 ; trap_score_get (1 in, 1 out)
pop unk ; unknown
```






### trap_mission_set_watch

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 39 ; trap_mission_set_watch (2 in, 0 out)

```






### trap_mission_get_timer_second

_Format:_

```
push unk1 ; unknown
syscall 4, 40 ; trap_mission_get_timer_second (1 in, 1 out)
pop unk ; unknown
```






### trap_mission_add_count

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 41 ; trap_mission_add_count (2 in, 0 out)

```






### trap_struggle_increment

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 42 ; trap_struggle_increment (2 in, 1 out)
pop unk ; unknown
```






### trap_mission_set_max_combo_counter

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 43 ; trap_mission_set_max_combo_counter (2 in, 0 out)

```






### trap_mission_disable_count

_Format:_

```
push unk1 ; unknown
syscall 4, 44 ; trap_mission_disable_count (1 in, 0 out)

```






### trap_mission_disable_watch

_Format:_

```
push unk1 ; unknown
syscall 4, 45 ; trap_mission_disable_watch (1 in, 0 out)

```






### trap_mission_set_warning_se

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 46 ; trap_mission_set_warning_se (2 in, 0 out)

```






### trap_mission_warning_timer

_Format:_

```
push unk1 ; unknown
syscall 4, 47 ; trap_mission_warning_timer (1 in, 0 out)

```






### trap_mission_set_count_figure_num

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 4, 48 ; trap_mission_set_count_figure_num (3 in, 0 out)

```






### trap_mission_disable_timer

_Format:_

```
push unk1 ; unknown
syscall 4, 49 ; trap_mission_disable_timer (1 in, 0 out)

```






### trap_mission_warning_count

_Format:_

```
push unk1 ; unknown
syscall 4, 50 ; trap_mission_warning_count (1 in, 0 out)

```






### trap_mission_set_combo_counter_param

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 4, 51 ; trap_mission_set_combo_counter_param (4 in, 0 out)

```






### trap_mission_warning_combo_counter

_Format:_

```
push unk1 ; unknown
syscall 4, 52 ; trap_mission_warning_combo_counter (1 in, 0 out)

```






### trap_mission_set_combo_counter_warning_se

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 53 ; trap_mission_set_combo_counter_warning_se (2 in, 0 out)

```






### trap_mission_lock

_Format:_

```
syscall 4, 54 ; trap_mission_lock (0 in, 0 out)

```






### trap_mission_is_lock

_Format:_

```
syscall 4, 55 ; trap_mission_is_lock (0 in, 1 out)
pop unk ; unknown
```






### trap_event_continue_control_off

_Format:_

```
syscall 4, 56 ; trap_event_continue_control_off (0 in, 0 out)

```






### trap_mission_warning_gauge

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 4, 57 ; trap_mission_warning_gauge (2 in, 0 out)

```






### trap_mission_reset_warning_count

_Format:_

```
push unk1 ; unknown
syscall 4, 58 ; trap_mission_reset_warning_count (1 in, 0 out)

```






### trap_get_start_rtn_action

_Format:_

```
push unk1 ; unknown
syscall 5, 0 ; trap_get_start_rtn_action (1 in, 1 out)
pop unk ; unknown
```






### trap_set_path_way

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 1 ; trap_set_path_way (2 in, 0 out)

```






### trap_reverse_path_way

_Format:_

```
push unk1 ; unknown
syscall 5, 2 ; trap_reverse_path_way (1 in, 1 out)
pop unk ; unknown
```






### trap_get_path_dir

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 3 ; trap_get_path_dir (2 in, 1 out)
pop unk ; unknown
```






### trap_end_rtn_action

_Format:_

```
push unk1 ; unknown
syscall 5, 4 ; trap_end_rtn_action (1 in, 0 out)

```






### trap_get_rtn_action

_Format:_

```
push unk1 ; unknown
syscall 5, 5 ; trap_get_rtn_action (1 in, 1 out)
pop unk ; unknown
```






### trap_get_rtn_action_dir

_Format:_

```
push unk1 ; unknown
syscall 5, 6 ; trap_get_rtn_action_dir (1 in, 1 out)
pop unk ; unknown
```






### trap_is_rtn_change_dir

_Format:_

```
push unk1 ; unknown
syscall 5, 7 ; trap_is_rtn_change_dir (1 in, 1 out)
pop unk ; unknown
```






### trap_create_active_path

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 8 ; trap_create_active_path (2 in, 0 out)

```






### trap_get_path_dir_from_obj

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 5, 9 ; trap_get_path_dir_from_obj (3 in, 1 out)
pop unk ; unknown
```






### trap_forward_path_current_pointer

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 10 ; trap_forward_path_current_pointer (2 in, 0 out)

```






### trap_is_end_rtn_action

_Format:_

```
push unk1 ; unknown
syscall 5, 11 ; trap_is_end_rtn_action (1 in, 1 out)
pop unk ; unknown
```






### trap_reset_active_path

_Format:_

```
push unk1 ; unknown
syscall 5, 12 ; trap_reset_active_path (1 in, 0 out)

```






### trap_set_path_target_point

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 13 ; trap_set_path_target_point (2 in, 0 out)

```






### trap_get_path_point_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 14 ; trap_get_path_point_pos (2 in, 1 out)
pop unk ; unknown
```






### trap_clear_active_path

_Format:_

```
push unk1 ; unknown
syscall 5, 15 ; trap_clear_active_path (1 in, 0 out)

```






### trap_reset_leave_way

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 16 ; trap_reset_leave_way (2 in, 0 out)

```






### trap_check_rtn_option_flag

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 17 ; trap_check_rtn_option_flag (2 in, 1 out)
pop unk ; unknown
```






### trap_reset_path_current_pointer

_Format:_

```
push unk1 ; unknown
syscall 5, 18 ; trap_reset_path_current_pointer (1 in, 0 out)

```






### trap_get_path_current_pos

_Format:_

```
push unk1 ; unknown
syscall 5, 19 ; trap_get_path_current_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_get_path_current_dir

_Format:_

```
push unk1 ; unknown
syscall 5, 20 ; trap_get_path_current_dir (1 in, 1 out)
pop unk ; unknown
```






### trap_get_path_first_point_pos

_Format:_

```
push unk1 ; unknown
syscall 5, 21 ; trap_get_path_first_point_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_get_path_last_point_pos

_Format:_

```
push unk1 ; unknown
syscall 5, 22 ; trap_get_path_last_point_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_set_path_by_id

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 23 ; trap_set_path_by_id (2 in, 1 out)
pop unk ; unknown
```






### trap_set_path_by_group

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 24 ; trap_set_path_by_group (2 in, 1 out)
pop unk ; unknown
```






### trap_get_path_dir_r

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 5, 25 ; trap_get_path_dir_r (3 in, 1 out)
pop unk ; unknown
```






### trap_set_rtn_partner

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 26 ; trap_set_rtn_partner (2 in, 0 out)

```






### trap_set_rtn_option_flag

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 27 ; trap_set_rtn_option_flag (2 in, 0 out)

```






### trap_eh22_path_move_next

_Format:_

```
push unk1 ; unknown
syscall 5, 28 ; trap_eh22_path_move_next (1 in, 0 out)

```






### trap_eh22_path_move_before

_Format:_

```
push unk1 ; unknown
syscall 5, 29 ; trap_eh22_path_move_before (1 in, 0 out)

```






### trap_eh22_path_is_moving

_Format:_

```
push unk1 ; unknown
syscall 5, 30 ; trap_eh22_path_is_moving (1 in, 1 out)
pop unk ; unknown
```






### trap_eh22_path_get_point

_Format:_

```
push unk1 ; unknown
syscall 5, 31 ; trap_eh22_path_get_point (1 in, 1 out)
pop unk ; unknown
```






### trap_eh22_path_play

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 5, 32 ; trap_eh22_path_play (3 in, 0 out)

```






### trap_set_rtn_time_param

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 5, 33 ; trap_set_rtn_time_param (2 in, 0 out)

```






### trap_get_obj_head_pos

_Format:_

```
push unk1 ; unknown
syscall 5, 34 ; trap_get_obj_head_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_camera_shake

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
push unk6 ; unknown
push unk7 ; unknown
syscall 6, 0 ; trap_camera_shake (7 in, 0 out)

```






### trap_prize_appear

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 1 ; trap_prize_appear (2 in, 0 out)

```






### trap_player_get_form

_Format:_

```
syscall 6, 2 ; trap_player_get_form (0 in, 1 out)
pop unk ; unknown
```






### trap_target_searcher_init

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 3 ; trap_target_searcher_init (2 in, 0 out)

```






### trap_target_searcher_reset

_Format:_

```
push unk1 ; unknown
syscall 6, 4 ; trap_target_searcher_reset (1 in, 0 out)

```






### trap_target_seracher_search

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
push unk6 ; unknown
push unk7 ; unknown
syscall 6, 5 ; trap_target_seracher_search (7 in, 0 out)

```






### trap_obj_stop

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 6, 6 ; trap_obj_stop (3 in, 0 out)

```






### trap_obj_restart

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 7 ; trap_obj_restart (2 in, 0 out)

```






### trap_target_searcher_add

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 8 ; trap_target_searcher_add (2 in, 0 out)

```






### trap_target_dist

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 9 ; trap_target_dist (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_is_hit_attack

_Format:_

```
push unk1 ; unknown
syscall 6, 10 ; trap_obj_is_hit_attack (1 in, 1 out)
pop unk ; unknown
```






### trap_target_searcher_search_obj

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 6, 11 ; trap_target_searcher_search_obj (3 in, 0 out)

```






### trap_target_searcher_get_old

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 6, 12 ; trap_target_searcher_get_old (3 in, 0 out)

```






### trap_friend_force_warp

_Format:_

```
push unk1 ; unknown
syscall 6, 13 ; trap_friend_force_warp (1 in, 0 out)

```






### trap_friend_get

_Format:_

```
push unk1 ; unknown
syscall 6, 14 ; trap_friend_get (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_set_warp_level

_Format:_

```
push unk1 ; unknown
syscall 6, 15 ; trap_friend_set_warp_level (1 in, 0 out)

```






### trap_target_clear

_Format:_

```
push unk1 ; unknown
syscall 6, 16 ; trap_target_clear (1 in, 0 out)

```






### trap_lockon_show

_Format:_

```
syscall 6, 17 ; trap_lockon_show (0 in, 0 out)

```






### trap_lockon_hide

_Format:_

```
syscall 6, 18 ; trap_lockon_hide (0 in, 0 out)

```






### trap_status_peterpan_prize_drain_start

_Format:_

```
syscall 6, 19 ; trap_status_peterpan_prize_drain_start (0 in, 0 out)

```






### trap_status_peterpan_prize_drain_end

_Format:_

```
syscall 6, 20 ; trap_status_peterpan_prize_drain_end (0 in, 0 out)

```






### trap_target_searcher_add_target

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 21 ; trap_target_searcher_add_target (2 in, 0 out)

```






### trap_target_searcher_get_target_num

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 6, 22 ; trap_target_searcher_get_target_num (4 in, 1 out)
pop unk ; unknown
```






### trap_obj_near_parts

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 23 ; trap_obj_near_parts (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_get_bg_press

_Format:_

```
push unk1 ; unknown
syscall 6, 24 ; trap_obj_get_bg_press (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_tt_ball_blow

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 6, 25 ; trap_obj_tt_ball_blow (4 in, 0 out)

```






### trap_obj_limit_hover

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 6, 26 ; trap_obj_limit_hover (4 in, 0 out)

```






### trap_player_dice

_Format:_

```
syscall 6, 27 ; trap_player_dice (0 in, 0 out)

```






### trap_dice_set_spec

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 6, 28 ; trap_dice_set_spec (4 in, 0 out)

```






### trap_player_card

_Format:_

```
syscall 6, 29 ; trap_player_card (0 in, 0 out)

```






### trap_card_set_spec

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
push unk6 ; unknown
push unk7 ; unknown
syscall 6, 30 ; trap_card_set_spec (7 in, 0 out)

```






### trap_limit_aladdin_prize_drain

_Format:_

```
syscall 6, 31 ; trap_limit_aladdin_prize_drain (0 in, 0 out)

```






### trap_skateboard_ride

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 32 ; trap_skateboard_ride (2 in, 0 out)

```






### trap_skateboard_trick

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 6, 33 ; trap_skateboard_trick (3 in, 0 out)

```






### trap_skateboard_trick_motion_push

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 6, 34 ; trap_skateboard_trick_motion_push (3 in, 0 out)

```






### trap_obj_attach_camera

_Format:_

```
push unk1 ; unknown
syscall 6, 35 ; trap_obj_attach_camera (1 in, 0 out)

```






### trap_obj_detach_camera

_Format:_

```
push unk1 ; unknown
syscall 6, 36 ; trap_obj_detach_camera (1 in, 0 out)

```






### trap_obj_is_attach_camera

_Format:_

```
push unk1 ; unknown
syscall 6, 37 ; trap_obj_is_attach_camera (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_limit_mulan_idle

_Format:_

```
push unk1 ; unknown
syscall 6, 38 ; trap_obj_limit_mulan_idle (1 in, 0 out)

```






### trap_skateboard_ride_edge

_Format:_

```
push unk1 ; unknown
syscall 6, 39 ; trap_skateboard_ride_edge (1 in, 0 out)

```






### trap_obj_limit_peterpan_idle

_Format:_

```
push unk1 ; unknown
syscall 6, 40 ; trap_obj_limit_peterpan_idle (1 in, 0 out)

```






### trap_skateboard_edge_jump

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 6, 41 ; trap_skateboard_edge_jump (3 in, 0 out)

```






### trap_obj_hop_direct

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 6, 42 ; trap_obj_hop_direct (4 in, 0 out)

```






### trap_command_limit_trinity_commbo_start

_Format:_

```
push unk1 ; unknown
syscall 6, 43 ; trap_command_limit_trinity_commbo_start (1 in, 0 out)

```






### trap_obj_limit_riku_idle

_Format:_

```
push unk1 ; unknown
syscall 6, 44 ; trap_obj_limit_riku_idle (1 in, 0 out)

```






### trap_obj_hide_shadow

_Format:_

```
push unk1 ; unknown
syscall 6, 45 ; trap_obj_hide_shadow (1 in, 0 out)

```






### trap_obj_rc_stop_all

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 6, 46 ; trap_obj_rc_stop_all (4 in, 0 out)

```






### trap_obj_stop_end_all

_Format:_

```
push unk1 ; unknown
syscall 6, 47 ; trap_obj_stop_end_all (1 in, 0 out)

```






### trap_skateboardscore_add_count

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 48 ; trap_skateboardscore_add_count (2 in, 0 out)

```






### trap_obj_is_stop

_Format:_

```
push unk1 ; unknown
syscall 6, 49 ; trap_obj_is_stop (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_stop_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 50 ; trap_obj_stop_start (2 in, 0 out)

```






### trap_bghit_check_line

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 6, 51 ; trap_bghit_check_line (4 in, 1 out)
pop unk ; unknown
```






### trap_bghit_get_normal

_Format:_

```
push unk1 ; unknown
syscall 6, 52 ; trap_bghit_get_normal (1 in, 1 out)
pop unk ; unknown
```






### trap_bghit_is_hit

_Format:_

```
push unk1 ; unknown
syscall 6, 53 ; trap_bghit_is_hit (1 in, 1 out)
pop unk ; unknown
```






### trap_bghit_get_cross_pos

_Format:_

```
push unk1 ; unknown
syscall 6, 54 ; trap_bghit_get_cross_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_bghit_get_kind

_Format:_

```
push unk1 ; unknown
syscall 6, 55 ; trap_bghit_get_kind (1 in, 1 out)
pop unk ; unknown
```






### trap_target_set_group

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 56 ; trap_target_set_group (2 in, 0 out)

```






### trap_target_get_group

_Format:_

```
push unk1 ; unknown
syscall 6, 57 ; trap_target_get_group (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_act_child_push

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 58 ; trap_obj_act_child_push (2 in, 0 out)

```






### trap_xemnas_get_obj

_Format:_

```
push unk1 ; unknown
syscall 6, 59 ; trap_xemnas_get_obj (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_stealth_color

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 6, 60 ; trap_obj_set_stealth_color (4 in, 0 out)

```






### trap_obj_is_hook

_Format:_

```
push unk1 ; unknown
syscall 6, 61 ; trap_obj_is_hook (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_carpet_obj_idle

_Format:_

```
push unk1 ; unknown
syscall 6, 62 ; trap_obj_carpet_obj_idle (1 in, 0 out)

```






### trap_obj_is_damage_motion

_Format:_

```
push unk1 ; unknown
syscall 6, 63 ; trap_obj_is_damage_motion (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_show_shadow

_Format:_

```
push unk1 ; unknown
syscall 6, 64 ; trap_obj_show_shadow (1 in, 0 out)

```






### trap_obj_set_scissoring

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 65 ; trap_obj_set_scissoring (2 in, 0 out)

```






### trap_obj_clear_hitback

_Format:_

```
push unk1 ; unknown
syscall 6, 66 ; trap_obj_clear_hitback (1 in, 0 out)

```






### trap_obj_party_attack

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 67 ; trap_obj_party_attack (2 in, 0 out)

```






### trap_strike_raid_calc_xyzrot

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 68 ; trap_strike_raid_calc_xyzrot (2 in, 1 out)
pop unk ; unknown
```






### trap_larxene_dead

_Format:_

```
push unk1 ; unknown
syscall 6, 69 ; trap_larxene_dead (1 in, 0 out)

```






### trap_obj_play_se_loop

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 70 ; trap_obj_play_se_loop (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_fadeout_se

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 6, 71 ; trap_obj_fadeout_se (2 in, 0 out)

```






### trap_enemy_stop_all_start

_Format:_

```
push unk1 ; unknown
syscall 7, 0 ; trap_enemy_stop_all_start (1 in, 0 out)

```






### trap_enemy_stop_all_end

_Format:_

```
push unk1 ; unknown
syscall 7, 1 ; trap_enemy_stop_all_end (1 in, 0 out)

```






### trap_attack_hit_mark_pos

_Format:_

```
push unk1 ; unknown
syscall 7, 2 ; trap_attack_hit_mark_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_flare_init

_Format:_

```
syscall 7, 3 ; trap_flare_init (0 in, 0 out)

```






### trap_flare_new

_Format:_

```
syscall 7, 4 ; trap_flare_new (0 in, 1 out)
pop unk ; unknown
```






### trap_flare_free

_Format:_

```
push unk1 ; unknown
syscall 7, 5 ; trap_flare_free (1 in, 0 out)

```






### trap_flare_set_pos

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 6 ; trap_flare_set_pos (2 in, 0 out)

```






### trap_flare_set_radius

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 7, 7 ; trap_flare_set_radius (3 in, 0 out)

```






### trap_flare_set_effect

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 8 ; trap_flare_set_effect (2 in, 0 out)

```






### trap_flare_set_target

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 9 ; trap_flare_set_target (2 in, 0 out)

```






### trap_flare_get_pos

_Format:_

```
push unk1 ; unknown
syscall 7, 10 ; trap_flare_get_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_flare_is_empty

_Format:_

```
syscall 7, 11 ; trap_flare_is_empty (0 in, 1 out)
pop unk ; unknown
```






### trap_limit_aladdin_exclamation_mark_pos

_Format:_

```
push unk1 ; unknown
syscall 7, 12 ; trap_limit_aladdin_exclamation_mark_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_magic_calc_speed

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 7, 13 ; trap_magic_calc_speed (4 in, 1 out)
pop unk ; unknown
```






### trap_attack_set_reaction_offset

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 14 ; trap_attack_set_reaction_offset (2 in, 0 out)

```






### trap_friend_get_target_size

_Format:_

```
push unk1 ; unknown
syscall 7, 15 ; trap_friend_get_target_size (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_get_current_action

_Format:_

```
push unk1 ; unknown
syscall 7, 16 ; trap_friend_get_current_action (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_set_script_status

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 17 ; trap_friend_set_script_status (2 in, 1 out)
pop unk ; unknown
```






### trap_friend_get_main_status

_Format:_

```
push unk1 ; unknown
syscall 7, 18 ; trap_friend_get_main_status (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_update_target

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 19 ; trap_friend_update_target (2 in, 1 out)
pop unk ; unknown
```






### trap_obj_limit_hover_set_spec

_Format:_

```
push unk1 ; unknown
syscall 7, 21 ; trap_obj_limit_hover_set_spec (1 in, 0 out)

```






### trap_friend_enable_system_wishdir

_Format:_

```
push unk1 ; unknown
syscall 7, 24 ; trap_friend_enable_system_wishdir (1 in, 0 out)

```






### trap_friend_disable_system_wishdir

_Format:_

```
push unk1 ; unknown
syscall 7, 25 ; trap_friend_disable_system_wishdir (1 in, 0 out)

```






### trap_friend_call

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 26 ; trap_friend_call (2 in, 1 out)
pop unk ; unknown
```






### trap_limit_start_command

_Format:_

```
syscall 7, 27 ; trap_limit_start_command (0 in, 1 out)
pop unk ; unknown
```






### trap_trinity_shot_init

_Format:_

```
syscall 7, 28 ; trap_trinity_shot_init (0 in, 0 out)

```






### trap_trinity_shot_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 7, 29 ; trap_trinity_shot_start (4 in, 1 out)
pop unk ; unknown
```






### trap_trinity_shot_ensure

_Format:_

```
syscall 7, 30 ; trap_trinity_shot_ensure (0 in, 0 out)

```






### trap_trinity_shot_set_effect_id

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 31 ; trap_trinity_shot_set_effect_id (2 in, 0 out)

```






### trap_vacuum_set_effective_range

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 32 ; trap_vacuum_set_effective_range (2 in, 0 out)

```






### trap_enemy_summon_entry

_Format:_

```
push unk1 ; unknown
syscall 7, 33 ; trap_enemy_summon_entry (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_set_rc_owner

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 7, 34 ; trap_attack_set_rc_owner (2 in, 0 out)

```






### trap_summon_is_exec

_Format:_

```
syscall 7, 35 ; trap_summon_is_exec (0 in, 1 out)
pop unk ; unknown
```






### trap_limit_reset_hit_counter

_Format:_

```
push unk1 ; unknown
syscall 7, 36 ; trap_limit_reset_hit_counter (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_target_radius

_Format:_

```
push unk1 ; unknown
syscall 8, 0 ; trap_obj_target_radius (1 in, 1 out)
pop unk ; unknown
```






### trap_player_push_ability_button

_Format:_

```
push unk1 ; unknown
syscall 8, 1 ; trap_player_push_ability_button (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_xyzrot

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 8, 2 ; trap_obj_set_xyzrot (2 in, 0 out)

```






### trap_special_last_xemnus_laser_start

_Format:_

```
push unk1 ; unknown
syscall 8, 3 ; trap_special_last_xemnus_laser_start (1 in, 0 out)

```






### trap_special_last_xemnus_laser_attack

_Format:_

```
syscall 8, 4 ; trap_special_last_xemnus_laser_attack (0 in, 0 out)

```






### trap_special_last_xemnus_laser_end

_Format:_

```
syscall 8, 5 ; trap_special_last_xemnus_laser_end (0 in, 0 out)

```






### trap_special_last_xemnus_laser_optimize

_Format:_

```
syscall 8, 6 ; trap_special_last_xemnus_laser_optimize (0 in, 0 out)

```






### trap_special_last_xemnus_laser_optimize_end

_Format:_

```
syscall 8, 7 ; trap_special_last_xemnus_laser_optimize_end (0 in, 0 out)

```






### trap_camera_apply_inverse_pos

_Format:_

```
push unk1 ; unknown
syscall 8, 8 ; trap_camera_apply_inverse_pos (1 in, 1 out)
pop unk ; unknown
```






### trap_empty_func

_Format:_

```
syscall 10, 0 ; trap_empty_func (0 in, 0 out)

```






### trap_stitch_set_screen_position

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 1 ; trap_stitch_set_screen_position (2 in, 0 out)

```






### trap_stitch_get_screen_position

_Format:_

```
push unk1 ; unknown
syscall 10, 2 ; trap_stitch_get_screen_position (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_start_limit

_Format:_

```
push unk1 ; unknown
syscall 10, 3 ; trap_friend_start_limit (1 in, 0 out)

```






### trap_friend_end_limit

_Format:_

```
push unk1 ; unknown
syscall 10, 4 ; trap_friend_end_limit (1 in, 0 out)

```






### trap_chickenlittle_get_shoot_target

_Format:_

```
push unk1 ; unknown
syscall 10, 5 ; trap_chickenlittle_get_shoot_target (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_special_command

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 6 ; trap_obj_set_special_command (2 in, 0 out)

```






### trap_obj_reset_special_command

_Format:_

```
push unk1 ; unknown
syscall 10, 7 ; trap_obj_reset_special_command (1 in, 0 out)

```






### trap_friend_get_target_last_position

_Format:_

```
push unk1 ; unknown
syscall 10, 8 ; trap_friend_get_target_last_position (1 in, 1 out)
pop unk ; unknown
```






### trap_genie_change_form

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 9 ; trap_genie_change_form (2 in, 0 out)

```






### trap_genie_get_limit_command

_Format:_

```
push unk1 ; unknown
syscall 10, 10 ; trap_genie_get_limit_command (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_stop_timer

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 10, 11 ; trap_obj_set_stop_timer (3 in, 0 out)

```






### trap_stitch_effect_start

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
push unk5 ; unknown
push unk6 ; unknown
push unk7 ; unknown
push unk8 ; unknown
syscall 10, 12 ; trap_stitch_effect_start (8 in, 1 out)
pop unk ; unknown
```






### trap_stitch_shot_effect

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 13 ; trap_stitch_shot_effect (2 in, 0 out)

```






### trap_friend_set_target

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 10, 14 ; trap_friend_set_target (3 in, 0 out)

```






### trap_sysobj_motion_cont_push

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 10, 15 ; trap_sysobj_motion_cont_push (3 in, 0 out)

```






### trap_stitch_effect_kill

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 16 ; trap_stitch_effect_kill (2 in, 0 out)

```






### trap_sysobj_is_zako

_Format:_

```
push unk1 ; unknown
syscall 10, 17 ; trap_sysobj_is_zako (1 in, 1 out)
pop unk ; unknown
```






### trap_sysobj_is_boss

_Format:_

```
push unk1 ; unknown
syscall 10, 18 ; trap_sysobj_is_boss (1 in, 1 out)
pop unk ; unknown
```






### trap_sysobj_is_limit

_Format:_

```
push unk1 ; unknown
syscall 10, 19 ; trap_sysobj_is_limit (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_follow_player

_Format:_

```
push unk1 ; unknown
syscall 10, 20 ; trap_friend_follow_player (1 in, 0 out)

```






### trap_friend_follow_enemy

_Format:_

```
push unk1 ; unknown
syscall 10, 21 ; trap_friend_follow_enemy (1 in, 0 out)

```






### trap_sysobj_is_blow

_Format:_

```
push unk1 ; unknown
syscall 10, 22 ; trap_sysobj_is_blow (1 in, 1 out)
pop unk ; unknown
```






### trap_enemy_is_attacked_from

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 23 ; trap_enemy_is_attacked_from (2 in, 1 out)
pop unk ; unknown
```






### tarp_friend_is_equiped_ability

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 24 ; tarp_friend_is_equiped_ability (2 in, 1 out)
pop unk ; unknown
```






### trap_peterpan_receive_notify_player_target

_Format:_

```
push unk1 ; unknown
syscall 10, 25 ; trap_peterpan_receive_notify_player_target (1 in, 1 out)
pop unk ; unknown
```






### trap_peterpan_accept_notify_player_target

_Format:_

```
push unk1 ; unknown
syscall 10, 26 ; trap_peterpan_accept_notify_player_target (1 in, 0 out)

```






### trap_friend_enable_inertia

_Format:_

```
push unk1 ; unknown
syscall 10, 27 ; trap_friend_enable_inertia (1 in, 0 out)

```






### trap_friend_disable_inertia

_Format:_

```
push unk1 ; unknown
syscall 10, 28 ; trap_friend_disable_inertia (1 in, 0 out)

```






### trap_friend_use_item

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 10, 29 ; trap_friend_use_item (4 in, 0 out)

```






### trap_sysobj_is_finish_blow

_Format:_

```
push unk1 ; unknown
syscall 10, 30 ; trap_sysobj_is_finish_blow (1 in, 1 out)
pop unk ; unknown
```






### trap_sysobj_is_summon

_Format:_

```
push unk1 ; unknown
syscall 10, 31 ; trap_sysobj_is_summon (1 in, 1 out)
pop unk ; unknown
```






### trap_stitch_move_request

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 32 ; trap_stitch_move_request (2 in, 0 out)

```






### trap_friend_get_player_attacker

_Format:_

```
push unk1 ; unknown
syscall 10, 33 ; trap_friend_get_player_attacker (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_remove_player_attacker

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 34 ; trap_friend_remove_player_attacker (2 in, 0 out)

```






### trap_friend_get_action_param

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 35 ; trap_friend_get_action_param (2 in, 1 out)
pop unk ; unknown
```






### trap_friend_is_control

_Format:_

```
push unk1 ; unknown
syscall 10, 36 ; trap_friend_is_control (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_is_moveonly

_Format:_

```
push unk1 ; unknown
syscall 10, 37 ; trap_friend_is_moveonly (1 in, 1 out)
pop unk ; unknown
```






### trap_attack_is_finish

_Format:_

```
push unk1 ; unknown
syscall 10, 38 ; trap_attack_is_finish (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_action_clear

_Format:_

```
push unk1 ; unknown
syscall 10, 39 ; trap_friend_action_clear (1 in, 0 out)

```






### trap_obj_is_motion_sync

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 40 ; trap_obj_is_motion_sync (2 in, 1 out)
pop unk ; unknown
```






### trap_friend_start_leave

_Format:_

```
push unk1 ; unknown
syscall 10, 41 ; trap_friend_start_leave (1 in, 0 out)

```






### trap_friend_is_start_leave

_Format:_

```
push unk1 ; unknown
syscall 10, 42 ; trap_friend_is_start_leave (1 in, 1 out)
pop unk ; unknown
```






### trap_obj_set_use_mp

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 43 ; trap_obj_set_use_mp (2 in, 0 out)

```






### trap_obj_is_tornado

_Format:_

```
push unk1 ; unknown
syscall 10, 44 ; trap_obj_is_tornado (1 in, 1 out)
pop unk ; unknown
```






### trap_sheet_get_drive_time

_Format:_

```
push unk1 ; unknown
syscall 10, 45 ; trap_sheet_get_drive_time (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_disable_follow_enemy

_Format:_

```
push unk1 ; unknown
syscall 10, 46 ; trap_friend_disable_follow_enemy (1 in, 0 out)

```






### trap_friend_enable_follow_enemy

_Format:_

```
push unk1 ; unknown
syscall 10, 47 ; trap_friend_enable_follow_enemy (1 in, 0 out)

```






### trap_friend_disable_follow_player

_Format:_

```
push unk1 ; unknown
syscall 10, 48 ; trap_friend_disable_follow_player (1 in, 0 out)

```






### trap_friend_enable_follow_player

_Format:_

```
push unk1 ; unknown
syscall 10, 49 ; trap_friend_enable_follow_player (1 in, 0 out)

```






### trap_sheet_get_mp

_Format:_

```
push unk1 ; unknown
syscall 10, 50 ; trap_sheet_get_mp (1 in, 1 out)
pop unk ; unknown
```






### trap_chickenlittle_get_nearest_target

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
push unk4 ; unknown
syscall 10, 51 ; trap_chickenlittle_get_nearest_target (4 in, 0 out)

```






### trap_btlobj_is_reflect_motion

_Format:_

```
push unk1 ; unknown
syscall 10, 52 ; trap_btlobj_is_reflect_motion (1 in, 1 out)
pop unk ; unknown
```






### trap_friend_add_watch_effect

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 53 ; trap_friend_add_watch_effect (2 in, 0 out)

```






### trap_friend_is_effect_exist

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 54 ; trap_friend_is_effect_exist (2 in, 1 out)
pop unk ; unknown
```






### trap_target_searcher_set_check_hide_from_friend

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 55 ; trap_target_searcher_set_check_hide_from_friend (2 in, 0 out)

```






### trap_friend_invalidate_warp_point

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 56 ; trap_friend_invalidate_warp_point (2 in, 0 out)

```






### trap_friend_add_warp_point

_Format:_

```
push unk1 ; unknown
syscall 10, 57 ; trap_friend_add_warp_point (1 in, 0 out)

```






### trap_friend_link_magic

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
push unk3 ; unknown
syscall 10, 58 ; trap_friend_link_magic (3 in, 0 out)

```






### trap_chickenlittle_set_shoot_target

_Format:_

```
push unk1 ; unknown
push unk2 ; unknown
syscall 10, 59 ; trap_chickenlittle_set_shoot_target (2 in, 0 out)

```






