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
			IorD		: out std_logic; -- Additional signal to select the next address (PC = '0' or Rs1 = '1')
			Cu_state 	: out std_logic_vector(3 downto 0)
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
				ALU_op 		<= "0000"; 
				ALU_src1 	<= '0';
				ALU_src2 	<= "00";
				Jmp_enable	<= '0';
				IorD			<= '0';
				Cu_state		<= "0000";
				nextState 	<= FETCH;
				
			when FETCH => 
				MemtoReg		<= '0'; --irrelevant
				GPRF_wr		<= '0'; 
				IR_write 	<= '1';
				Mem_wr 		<= '0';
				Rs2_select	<= '0'; --irrelevant
				PC_Wcond 	<= '0'; --irrelevant
				Mem_read 	<= '1';
				PC_write 	<= '1'; -- to increase PC by 1
				PC_source	<= '0';
				ALU_op 		<= ALU_ADD;
				ALU_src1 	<= sel_PC; -- choosing PC as source 1
				ALU_src2 	<= sel_1;  -- choosing 1 to add to PC	
				Jmp_enable	<= '0';
				IorD			<= '0';
				Cu_state		<= "0001";
				nextState 	<= DECODE;
			
			
			when DECODE => 
				MemtoReg		<= '0'; --irrelevant
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= Operation(to_integer(unsigned(JZ))) OR Operation(to_integer(unsigned(JNZ))); -- set Rs2_select to '1' when JZ or JNZ occur otherwise '0'
				PC_Wcond 	<= '0'; --irrelevant
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '0'; --irrelevant
				ALU_op 		<= ALU_ADD;
				ALU_src1 	<= sel_PC; -- choosing PC as source 1
				ALU_src2 	<= sel_Imm;  -- choosing Immediate to add to PC
				Jmp_enable	<= '0';	
				IorD			<= '0'; --irrelevant
				Cu_state		<= "0010";
				
				if Operation(to_integer(unsigned(JUMP))) = '1' then 
				
					nextState 	<= JTYPE;
					
				elsif Operation(to_integer(unsigned(JZ))) = '1' then
				
					nextState 	<= JZTYPE;
					
				elsif Operation(to_integer(unsigned(JNZ))) = '1' then
				
					nextState 	<= JNZTYPE;
					
				elsif Operation(to_integer(unsigned(LOAD))) = '1' OR Operation(to_integer(unsigned(STORE))) = '1' then
				
					nextState 	<= MEM_ACCESS;
					
				elsif Operation(to_integer(unsigned(NOP))) = '1' then
				
					nextState 	<= FETCH;
		
				else
				
					nextState 	<= RTYPE;
		
				end if;
				
			when JTYPE => 
				MemtoReg		<= '0'; --irrelevant
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '0'; --irrelevant
				PC_Wcond 	<= '0'; --irrelevant
				Mem_read 	<= '0';
				PC_write 	<= '1';
				PC_source	<= '1'; -- selecting ALU_OUT register to write to PC
				-- ALU is irrelevant for JTYPE state
				ALU_op 		<= "0000"; --irrelevant
				ALU_src1 	<= '0'; --irrelevant 
				ALU_src2 	<= "00"; --irrelevant
				Jmp_enable	<= '0';
				IorD			<= '0';
				Cu_state		<= "0011";
				nextState 	<= FETCH;
				
			when JZTYPE => 
				MemtoReg		<= '0'; --irrelevant
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '1'; -- read Rd from Register File
				PC_Wcond 	<= '1'; -- when '1', checks for JZ
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '1';
				ALU_op 		<= ALU_CMP;     
				ALU_src1 	<= '0'; 		 -- irrelevant because not used
				ALU_src2 	<= sel_Rs2;  -- choosing Rs2 to check zero flag		
				Jmp_enable	<= '1';
				IorD			<= '0';
				Cu_state		<= "0100";
				nextState 	<= FETCH;
				
			when JNZTYPE => 
				MemtoReg		<= '0'; --irrelevant
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '1'; -- read Rd from Register File
				PC_Wcond 	<= '0'; -- when '0', checks for JNZ
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '1';
				ALU_op 		<= ALU_CMP;   
				ALU_src1 	<= '0'; 		 -- irrelevant because not used
				ALU_src2 	<= sel_Rs2;  -- choosing Rs2 to check zero flag	
				Jmp_enable	<= '1';
				IorD			<= '0';
				Cu_state		<= "0101";
				nextState 	<= FETCH;
		
			when MEM_ACCESS =>
				MemtoReg		<= '0'; --irrelevant
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= Operation(to_integer(unsigned(STORE))); -- if there is STORE inst., enable memory write
				Rs2_select	<= '0'; --irrelevant 
				PC_Wcond 	<= '0'; --irrelevant
				Mem_read 	<= Operation(to_integer(unsigned(LOAD))); -- if there is LOAD inst., enable memory read
				PC_write 	<= '0';
				PC_source	<= '0'; --irrelevant
				ALU_op 		<= "0000";  -- irrelevant because not used   
				ALU_src1 	<= '0'; 		 -- irrelevant because not used
				ALU_src2 	<= "00";  -- irrelevant because not used	
				Jmp_enable	<= '0';
				IorD			<= '1'; -- Read memory address shown in Rs1
				Cu_state		<= "0110";
				
				if Operation(to_integer(unsigned(LOAD))) = '1' then 
				
					nextState 	<= WRITEBACK;
					
				else 
				
					nextState 	<= FETCH;
			
				end if;
				
			when RTYPE =>
				-- for RTYPE state, only ALU matters
				MemtoReg		<= '0'; --irrelevant
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '0'; --irrelevant 
				PC_Wcond 	<= '0'; --irrelevant 
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '0'; --irrelevant
				
				
				if Operation(to_integer(unsigned(ADD))) = '1' then 
					ALU_op 	<= ALU_ADD;  
					
				elsif Operation(to_integer(unsigned(SUBx))) = '1' then 
					ALU_op 	<= ALU_SUB;
					
				elsif Operation(to_integer(unsigned(ANDx))) = '1' then 
					ALU_op 	<= ALU_AND;
					
				elsif Operation(to_integer(unsigned(ORx))) = '1' then 
					ALU_op 	<= ALU_OR;
					
				elsif Operation(to_integer(unsigned(NOTx))) = '1' then 
					ALU_op 	<= ALU_NOT;
					
				elsif Operation(to_integer(unsigned(XORx))) = '1' then 
					ALU_op 	<= ALU_XOR;
					
				elsif Operation(to_integer(unsigned(CMP))) = '1' then 
					ALU_op 	<= ALU_CMP;
					
				elsif Operation(to_integer(unsigned(SHL))) = '1' then 
					ALU_op 	<= ALU_SHL;
					
				elsif Operation(to_integer(unsigned(SHR))) = '1' then 
					ALU_op 	<= ALU_SHR;
					
				elsif Operation(to_integer(unsigned(LOADI))) = '1' then 
					ALU_op 	<= ALU_SEL_SRC2;
					
				else 
					ALU_op 	<= "0000"; 
			
				end if;
				
				ALU_src1 	<= sel_Rs1; 
				-- for LOADI => sel_Imm ("10"), for others => sel_Rs2 ("00")
				ALU_src2 	<= Operation(to_integer(unsigned(LOADI))) & '0';  
				Jmp_enable	<= '0';
				IorD			<= '0';
				Cu_state		<= "0111";
				nextState 	<= WRITEBACK;
				
			when WRITEBACK => 
				MemtoReg		<= Operation(to_integer(unsigned(LOAD))); -- set to '1' only when LOAD occurs
				GPRF_wr		<= '1';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '0'; --irrelevant 
				PC_Wcond 	<= '0'; --irrelevant 
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '0'; --irrelevant
				ALU_op 		<= "0000";  --irrelevant
				ALU_src1 	<= '0'; 		--irrelevant	
				ALU_src2 	<= "00";  	--irrelevant
				Jmp_enable	<= '0';
				IorD			<= '0';
				Cu_state		<= "1000";
				nextState 	<= FETCH;
				
			when others => 
				MemtoReg		<= '0'; 
				GPRF_wr		<= '0';
				IR_write 	<= '0';
				Mem_wr 		<= '0';
				Rs2_select	<= '0'; 
				PC_Wcond 	<= '0'; 
				Mem_read 	<= '0';
				PC_write 	<= '0';
				PC_source	<= '0';
				ALU_op 		<= "0000";  
				ALU_src1 	<= '0'; 
				ALU_src2 	<= "00";  
				Jmp_enable	<= '0';
				IorD		<= '0';
				nextState 	<= START;
			
		
		end case;
	
	
	end process;


end RTL;