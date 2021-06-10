library IEEE;
use IEEE.std_logic_1164.all;

entity Reg is

	generic(
				DATA_WIDTH 	: integer := 16
	);

	port(
			Input		: in std_logic_vector((DATA_WIDTH-1) downto 0);
			CLK		: in std_logic;
			Reset 	: in std_logic;
			Enable	: in std_logic;
			Output	: out std_logic_vector((DATA_WIDTH-1) downto 0)
	
	);
	
end Reg;

architecture behavioral of Reg is
begin
	
	process(Input,CLK,Reset,Enable)
	
	begin
		
		if Reset = '1' then
			Output <= (others => '0');
			
		elsif rising_edge(CLK) and Enable = '1' then
			Output <= Input;
	
		end if;
	
	end process;

end behavioral;