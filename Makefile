PYTHON_VERSION = 3.5m
PYTHON_INCLUDE = /usr/include/python$(PYTHON_VERSION)

BOOST_INC = /usr/include
BOOST_LIB = /usr/lib

CXX = clang
CXXFLAGS = -g3 -ggdb -Wall -Wextra -Werror -Wno-long-long -Wno-variadic-macros -fexceptions -DNDEBUG -std=c++14 -O0 -pipe -fstack-protector-strong --param=ssp-buffer-size=4
LDFLAGS = -Wl,-O1,--sort-common,--as-needed,-z,relro,--export-dynamic
INCLUDES = -I . -I ${BOOST_INC} -I $(PYTHON_INCLUDE)
LIBS = -L$(BOOST_LIB) -L/usr/lib/python$(PYTHON_VERSION)/config -lpython3 -lboost_python3 -lboost_context

TARGET = mix

$(TARGET).so: $(TARGET).o
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(LIBS) -shared $(LDFLAGS) $(TARGET).o -o $(TARGET).so

$(TARGET).o: $(TARGET).cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -fPIC -c $(TARGET).cpp

clean:
	rm *.so *.o compile_commands.json
