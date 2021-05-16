library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity GPReg_File is
	
	generic(
				DATA_WIDTH 		: integer := 16;
				REG_ADDR_WIDTH : integer := 4
	);
	
	port(	
			Rs1 			: in std_logic_vector((REG_ADDR_WIDTH-1) downto 0);
			Rs2 			: in std_logic_vector((REG_ADDR_WIDTH-1) downto 0);
			Rd  			: in std_logic_vector((REG_ADDR_WIDTH-1) downto 0);
			GPRF_wr 		: in std_logic;
			data_in 		: in std_logic_vector((DATA_WIDTH-1) downto 0);
			CLK			: in std_logic;
			Reset 		: in std_logic;
			data_Rs1 	: out std_logic_vector((DATA_WIDTH-1) downto 0);
			data_Rs2 	: out std_logic_vector((DATA_WIDTH-1) downto 0)
		);

end GPReg_File;

architecture RTL of GPReg_File is
	-- defining an array for registers from 0 to 15
	subtype WORD is std_logic_vector((DATA_WIDTH-1) downto 0);
	type RegisterType is array (0 to (2**REG_ADDR_WIDTH-1)) of WORD;
	signal Registers : RegisterType := (others => (others => '0'));
	
begin

	Reg: process(CLK, Reset) 
	
	begin
	
		if Reset = '1' then
			Registers <= (others => (others => '0'));
		
		elsif rising_edge(CLK) then
			
			if GPRF_wr = '1' then
				Registers(to_integer(unsigned(Rd))) <= data_in;
			
			end if;
		
		end if;
	end process;
	
	Mux: process(Rs1, Rs2, Registers)
	
	begin
		
		data_Rs1 <= Registers(to_integer(unsigned(Rs1)));
		data_Rs2 <= Registers(to_integer(unsigned(Rs2)));

	
	end process;
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	



end RTL;