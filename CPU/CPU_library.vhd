library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

package CPU_library is
	
	--	GENERIC CONSTANTS --
	
	constant DATA_WIDTH 		: integer := 16;
	constant	REG_ADDR_WIDTH : integer := 4;
	
	-- INSTRUCTIONS --
	
	constant ADD	: std_logic_vector(3 downto 0) := "0000";
	constant SUBx	: std_logic_vector(3 downto 0) := "0001";
	constant ANDx	: std_logic_vector(3 downto 0) := "0010";
	constant ORx	: std_logic_vector(3 downto 0) := "0011";
	constant NOTx	: std_logic_vector(3 downto 0) := "0100";
	constant XORx	: std_logic_vector(3 downto 0) := "0101";
	constant CMP	: std_logic_vector(3 downto 0) := "0110";
	constant SHL	: std_logic_vector(3 downto 0) := "0111";
	constant SHR	: std_logic_vector(3 downto 0) := "1000";
	constant LOAD	: std_logic_vector(3 downto 0) := "1001";
	constant STORE	: std_logic_vector(3 downto 0) := "1010";
	constant JUMP	: std_logic_vector(3 downto 0) := "1011";
	constant NOP	: std_logic_vector(3 downto 0) := "1100";
	constant JZ		: std_logic_vector(3 downto 0) := "1101";
	constant JNZ	: std_logic_vector(3 downto 0) := "1110";
	constant LOADI	: std_logic_vector(3 downto 0) := "1111";


	-- FLAGS --
	
	-- CONTROL UNIT STATES --

	type state is (START, FETCH, DECODE, 
						JTYPE, JZTYPE, JNZTYPE,
						MEM_ACCESS, 
						RTYPE, WRITEBACK);
	
	-- ALU OPERATIONS --
	
	constant ALU_ADD			: std_logic_vector(3 downto 0) := "0000";
	constant ALU_SUB			: std_logic_vector(3 downto 0) := "0001";
	constant ALU_AND			: std_logic_vector(3 downto 0) := "0010";
	constant ALU_OR			: std_logic_vector(3 downto 0) := "0011";
	constant ALU_NOT			: std_logic_vector(3 downto 0) := "0100";
	constant ALU_XOR			: std_logic_vector(3 downto 0) := "0101";
	constant ALU_CMP			: std_logic_vector(3 downto 0) := "0110";
	constant ALU_SHL			: std_logic_vector(3 downto 0) := "0111";
	constant ALU_SHR			: std_logic_vector(3 downto 0) := "1000";
	constant ALU_SEL_SRC2	: std_logic_vector(3 downto 0) := "1001";
	
	
	
	
	
	-- ALU SOURCE SELECTION
	
	constant sel_Rs1	: std_logic := '0';
	constant sel_PC	: std_logic := '1';
	
	constant sel_Rs2	: std_logic_vector(1 downto 0) := "00";
	constant sel_1		: std_logic_vector(1 downto 0) := "01";
	constant sel_Imm	: std_logic_vector(1 downto 0) := "10";
	
	
	


end CPU_library;