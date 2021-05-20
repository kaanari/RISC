library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use work.CPU_library.all;

entity ControlUnit is
	
	port(	
			OpCode		: in std_logic_vector(3 downto 0);
			CLK			: in std_logic;
			Reset			: in std_logic;
			MemtoReg 	: out std_logic;
			GPRF_wr		: out std_logic;
			IR_write 	: out std_logic;
			Mem_wr		: out std_logic;
			Rs2_select	: out std_logic;
			PC_Wcond		: out std_logic;
			Mem_read		: out std_logic;
			PC_write 	: out std_logic;
			PC_source	: out std_logic;
			ALU_op		: out std_logic_vector(3 downto 0);
			ALU_src1		: out std_logic;
			ALU_src2		: out std_logic_vector(1 downto 0);
			Jmp_enable	: out std_logic; -- Additional output of CU for indicating that operitons JZ or JNZ is executing
			Cu_state 	: out std_logic
	);

end ControlUnit;

architecture RTL of ControlUnit is

	component OpcodeDecoder is

		port(
				OpCode : in std_logic_vector(3 downto 0);
				Operation : out std_logic_vector(15 downto 0)	
		);


	end component;

	signal currentState, nextState : state;
	signal Operation : std_logic_vector(15 downto 0);

begin

	OpDecoder: OpcodeDecoder port map(OpCode, Operation);

	state_reg: process(CLK, Reset)
	begin
	
		if Reset = '1' then
			
			currentState <= START;
		
		elsif rising_edge(CLK) then
		
			currentState <= nextState;
	
		end if;
	
	end process;
	
	control_signals: process(currentState)
	begin
	------------------------------ CU STATEEEEEEEE !!!!!!!!!!!!!!!!!!1------------
		case currentState is 
		
			when START => 
				MemtoReg		<= '0';
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '0';
				PC_Wcond 	<= '0';
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '0';
				ALU_op 		<= "0000"; -----CONTORL ETT !!!!
				ALU_src1 	<= sel_Rs1;
				ALU_src2 	<= sel_Rs2;
				Jmp_enable	<= '0';
				nextState 	<= FETCH;
				
			when FETCH => 
				MemtoReg		<= '0';
				GPRF_wr		<= '0';
				IR_write 	<= '1';
				Mem_wr 		<= '0';
				Rs2_select	<= '0';
				PC_Wcond 	<= '0';
				Mem_read 	<= '1';
				PC_write 	<= '1';
				PC_source	<= '0';
				ALU_op 		<= ALU_ADD;
				ALU_src1 	<= sel_PC; -- choosing PC as source 1
				ALU_src2 	<= sel_1;  -- choosing 1 to add to PC	
				Jmp_enable	<= '0';
				nextState 	<= DECODE;
			
			
			when DECODE => 
				MemtoReg		<= '0';
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= Operation(to_integer(unsigned(JZ))) OR Operation(to_integer(unsigned(JNZ))); -- set Rs2_select to '1' when JZ or JNZ occur otherwise '0'
				PC_Wcond 	<= '0';
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '0';
				ALU_op 		<= ALU_ADD;
				ALU_src1 	<= sel_PC; -- choosing PC as source 1
				ALU_src2 	<= sel_Imm;  -- choosing Immediate to add to PC
				Jmp_enable	<= '0';	
				
				if Operation(to_integer(unsigned(JMP))) = '1' then 
				
					nextState 	<= JTYPE;
					
				elsif Operation(to_integer(unsigned(JZ))) = '1' then
				
					nextState 	<= JZTYPE;
					
				elsif Operation(to_integer(unsigned(JNZ))) = '1' then
				
					nextState 	<= JNZTYPE;
					
				elsif Operation(to_integer(unsigned(LOAD))) = '1' OR Operation(to_integer(unsigned(STORE))) = '1' then
				
					nextState 	<= MEM_ADDRESS;
					
				elsif Operation(to_integer(unsigned(NOP))) = '1' then
				
					nextState 	<= FETCH;
		
				else
				
					nextState 	<= RTYPE;
		
				end if;
				
			when JTYPE => 
				MemtoReg		<= '0';
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '0';
				PC_Wcond 	<= '0';
				Mem_read 	<= '0';
				PC_write 	<= '1';
				PC_source	<= '1'; -- selecting ALU_OUT register to write to PC
				-- ALU is irrelevant for JTYPE state
				ALU_op 		<= "0000"
				ALU_src1 	<= '0'; 
				ALU_src2 	<= "00";  	
				nextState 	<= FETCH;
				
			when JZTYPE => 
				MemtoReg		<= '0';
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '1'; -- read Rd from Register File
				PC_Wcond 	<= '1'; -- when '1', checks for JZ
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '1';
				ALU_op 		<= "0000";  -- FIX ALU. COMPARE FALAN YAP.   
				ALU_src1 	<= '0'; 		 -- irrelevant because not used
				ALU_src2 	<= sel_Rs2;  -- choosing 1 to add to PC	
				Jmp_enable	<= '1';
				nextState 	<= FETCH;
				
			when JNZTYPE => 
				MemtoReg		<= '0';
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '1'; -- read Rd from Register File
				PC_Wcond 	<= '0'; -- when '0', checks for JNZ
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '1';
				ALU_op 		<= "0000";  -- FIX ALU. COMPARE FALAN YAP.   
				ALU_src1 	<= '0'; 		 -- irrelevant because not used
				ALU_src2 	<= sel_Rs2;  -- choosing 1 to add to PC	
				Jmp_enable	<= '1';
				nextState 	<= FETCH;
		
		
		
		end case;
	
	
	
	
	
	
	
	
	end process;




end RTL;