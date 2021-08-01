###  Sanitizers Python Native Module

##### Intro 
Python has great interoperability with C and C++ through extension modules. There are many reasons to do this, such as improving performance, <br />
accessing APIs not exposed by the language, or interfacing with libraries written in C or C++.

Unlike Python however, C and C++ are not memory safe. Luckily, great tools exist to help diagnose these kind of issues.<br />
One of those tools is ASan (Address Sanitizer) which uses compiler instrumentation to detect memory errors at runtime.

##### Type of Sanitizers

* AddressSanitizer - ASAN
* ThreadSanitizer - TSAN
* MemorySanitizer - MSAN
* UndefinedBehaviorSanitizer - UBSAN
* DataFlowSanitizer - DSAN


##### How to build
See wiki[https://github.com/google/sanitizers/wiki/AddressSanitizer] if you are interested in gory details. In general, to sanitize just a single module of large app you should compile and link it with `-fsanitize=address` <br />

```bash

$ CC="/usr/bin/clang" \ 
	CFLAGS="-fsanitize=address" \
	LDSHARED="clang -shared" \
	python3.9 ./setup.py install
```

##### asan_with_fuzzer.so  
So run application with LD_PRELOADed[https://github.com/google/sanitizers/wiki/AddressSanitizerAsDso#asan-and-ld_preload] libasan.so. 

```bash
LD_PRELOAD="$(pwd)/asan_with_fuzzer.so" python3.9
```

##### How to sanitizer ipv6_python source code

1- We need build `ipv6_python` python module - https://github.com/nasa/ipv6_python

```bash
$ cd ipv6_python
$ CC="/usr/bin/clang" \ 
	CFLAGS="-fsanitize=address" \
	LDSHARED="clang -shared" \
	python3.9 ./setup.py install

```
2-
```bash
>>> import ipv6
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: /usr/local/lib/python3.9/dist-packages/ipv6.cpython-39-x86_64-linux-gnu.so: undefined symbol: __asan_option_detect_stack_use_after_return
>>> 
```

So we see `undefined symbol: __asan_option_detect_stack_use_after_return` error, now i need `LD_PRELOAD` environmental variable for load `asan_with_fuzzer.so`.

```bash

$ LD_PRELOAD="$(pwd)/asan_with_fuzzer.so" python3.9
>>> import ipv6
>>> 
```


3- We write a small fuzzing program (called the “harness”) and create a programming environment to quickly integrate it into projects that consist of a callable set of functions,

```bash
$ cat harness.py 

import socket
import ipv6


host = "::1"
port = 3300
data = b"NASA"
resolve = socket.getaddrinfo(host, port, socket.AF_INET6, socket.SOCK_DGRAM)
(family, socktype, proto, _, sockaddr) = resolve[0]
sock = None #socket.socket(family, socktype, proto)
sockaddr = ipv6.get_flow_label(sock,*sockaddr)
print("Flow Label:",hex(sockaddr[2]))
sock.sendto(data,sockaddr)

```

4- run `harness.py ` 

```bash 
$ LD_PRELOAD="$(pwd)/asan_with_fuzzer.so" python3.9 harness.py                                                                               1 ⨯
AddressSanitizer:DEADLYSIGNAL
=================================================================
==3810==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000000 (pc 0x7f7f81a153c0 bp 0x7ffed0cd1ed0 sp 0x7ffed0cd1b60 T0)
==3810==The signal is caused by a READ memory access.
==3810==Hint: address points to the zero page.
    #0 0x7f7f81a153c0 in _Py_DECREF /usr/include/python3.9/object.h:422:13
    #1 0x7f7f81a153c0 in get_flow_label /home/fuzzing/Desktop/chapter04/ipv6_python/src/ipv6.c:144:7
    #2 0x53fc89  (/usr/bin/python3.9+0x53fc89)
    #3 0x53cdb8 in PyObject_Call (/usr/bin/python3.9+0x53cdb8)
    #4 0x51844b in _PyEval_EvalFrameDefault (/usr/bin/python3.9+0x51844b)
    #5 0x510d0c  (/usr/bin/python3.9+0x510d0c)
    #6 0x510ab6 in _PyEval_EvalCodeWithName (/usr/bin/python3.9+0x510ab6)
    #7 0x5f5042 in PyEval_EvalCode (/usr/bin/python3.9+0x5f5042)
    #8 0x619756  (/usr/bin/python3.9+0x619756)
    #9 0x614f7f  (/usr/bin/python3.9+0x614f7f)
    #10 0x6196e8  (/usr/bin/python3.9+0x6196e8)
    #11 0x619185 in PyRun_SimpleFileExFlags (/usr/bin/python3.9+0x619185)
    #12 0x60ca02 in Py_RunMain (/usr/bin/python3.9+0x60ca02)
    #13 0x5e9b48 in Py_BytesMain (/usr/bin/python3.9+0x5e9b48)
    #14 0x7f7f848c9d09 in __libc_start_main csu/../csu/libc-start.c:308:16
    #15 0x5e9a49 in _start (/usr/bin/python3.9+0x5e9a49)

AddressSanitizer can not provide additional info.
SUMMARY: AddressSanitizer: SEGV /usr/include/python3.9/object.h:422:13 in _Py_DECREF
==3810==ABORTING
                     
```

Now we discover `Null pointer dereference` bug,

![Crashed](https://github.com/raminfp/sanitizers_python_native_module/blob/main/img/ipv6_sanitize.png)

This bug Fixed - https://github.com/nasa/ipv6_python/commit/bc02ad0cc807437a9f178486c4584568b88055ff

Thanks,<br />
Ramin
