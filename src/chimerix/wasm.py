import wasmtime


def run_wat(wat_code: str, wasi: bool = False, func_name: str = "_start"):
    store = wasmtime.Store()
    linker = wasmtime.Linker(store.engine)

    if wasi:
        wasi_config = wasmtime.WasiConfig()
        wasi_config.inherit_stdout()
        wasi_config.inherit_stderr()
        store.set_wasi(wasi_config)
        linker.define_wasi()

    instance = linker.instantiate(
        store,
        wasmtime.Module(store.engine, wat_code),
    )

    func = instance.exports(store).get(func_name)
    if not isinstance(func, wasmtime.Func):
        print(f"incorrenct wasm: {func=}")
        return
    return func(store)


if __name__ == "__main__":
    run_wat(
        """
    (module
        (import "wasi_snapshot_preview1" "fd_write" 
            (func $fd_write (param i32 i32 i32 i32) (result i32)))
        (memory (export "memory") 1)
        (data (i32.const 0) "Hello, World!")
        (func (export "_start")
            (i32.store (i32.const 24) (i32.const 13))
            (i32.store (i32.const 20) (i32.const 0))
            (call $fd_write (i32.const 1) (i32.const 20) (i32.const 1) (i32.const 8))
            drop
        )
    )
    """,
        wasi=True,
    )
